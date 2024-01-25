import util
import LayoutParser
import copy


# Assumption 1: short and open do not happen in the same bump
# Assumption 2: at most 4 fault bumps
# format: key: [number of fault bump, number of short, number of open]
faultType = {
    '1short': [2, 1, 0],
    '2short_sequential': [3, 2, 0],
    '2short_parallel': [4, 2, 0],
    '3short': [4, 3, 0],
    '1open': [1, 0, 1],
    '2open': [2, 0, 2],
    '3open': [3, 0, 3],
    '1short1open': [3, 1, 1],
    '1short2open': [4, 1, 2],
    '2short1open': [4, 2, 1], # sequential short
}

# format key: [score reduction, need to repair or not, line color(for short), bump type(for open)]
Scoring = {
    'b': [0, False, 'chartreuse', ['Vss', 'Vdd']],
    'c': [1, True, 'fuchsia', ['Function']],
    'd': [1, False, 'orange', ['Spare']],
    'e': [2, True, 'black', []],
    'f': [2, False, 'blue', []],
}


class FaultBumpsList:
    def __init__(self, layout):

        self.fault_bumps_list = []
        self.initial_score_list = []
        self.bumps_per_bundle = []
        self.score_list = []
        self.larray = layout.construct_lmap()
        self.all_bump = layout.bump
        self.pass_after_repair = 0
        self.pass_before_repair = 0

    def __getitem__(self, idx=-1):
        if idx < 0 & idx > self.length:
            raise IndexError("list index out of range")
            return None
        else:
            return self.fault_bump[idx].__getitem__()

    def __len__(self):
        if self.length != len(self.bump):
            raise Exception('Length Error!!!')
        else:
            return self.length

    def remove_duplicate_sublists(self, input_list):
        unique_sublists = []
        seen_set = set()

        for sublist in input_list:
            # Convert each sublist to a frozenset for hashing
            sublist_frozenset = frozenset(sublist)

            # Check if the frozenset has been seen before
            if sublist_frozenset not in seen_set:
                # If not seen, add the frozenset to the set and the sublist to the result list
                seen_set.add(sublist_frozenset)
                unique_sublists.append(sublist)

        return unique_sublists

    def remove_duplicate_objects_in_vectors(self, input_list):
        result_list = []

        for vector in input_list:
            # Use a set to keep track of unique objects within the vector
            unique_objects_set = set()

            # Filter out duplicate objects and maintain the order
            unique_vector = [obj for obj in vector if obj not in unique_objects_set and not unique_objects_set.add(obj)]

            result_list.append(unique_vector)

        return result_list

    def find_short_lines(self, fault_type):
        short_list = []

        if fault_type=='1short' or fault_type=='1short1open' or fault_type=='1short2open':
            for line in self.larray:
                short_list.append([line])

        elif fault_type=='2short_sequential' or  fault_type=='2short1open':
            for line1 in self.larray:
                for line2 in self.larray:
                    if line1!=line2:
                        bump1a, bump1b = line1.link
                        bump2a, bump2b = line2.link
                        if bump1a==bump2a or bump1a==bump2b  or bump1b==bump2a or bump1b==bump2b :
                            short_list.append([line1, line2])
            short_list = self.remove_duplicate_sublists(short_list)

        elif fault_type=='2short_parallel':
            for line1 in self.larray:
                for line2 in self.larray:
                    if line1 != line2:
                        bump1a, bump1b = line1.link
                        bump2a, bump2b = line2.link
                        if bump1a!=bump2a and bump1a!=bump2b and bump1b!=bump2a and bump1b!=bump2b:
                            short_list.append([line1, line2])
            short_list = self.remove_duplicate_sublists(short_list)

        elif fault_type=='3short':
            for line1 in self.larray:
                for line2 in self.larray:
                            for line3 in self.larray:
                                if line1!=line2 and line2!=line3 and line1!=line3:
                                    bump1a, bump1b = line1.link
                                    bump2a, bump2b = line2.link
                                    bump3a, bump3b = line3.link
                                    short_list.append([line1, line2, line3])
            short_list = self.remove_duplicate_sublists(short_list)
        return short_list

    def find_short_bumps(self, short_list):
        short_bumps_list = []
        for short_lines in short_list:
            short_bumps = []
            for line in short_lines:
                bump1, bump2 = line.link
                short_bumps.append(bump1)
                short_bumps.append(bump2)
            short_bumps_list.append(short_bumps)
        short_bumps_list = self.remove_duplicate_objects_in_vectors(short_bumps_list)
        print('number of possible short: ', len(short_bumps_list))
        return short_bumps_list

    def find_open_given_short(self, fault_type, short_lines_list, short_bumps_list):
        open_bump_list = []
        fault_bumps_list = []
        if fault_type=='1open' or fault_type=='1short1open' or fault_type=='2short1open':
            if len(short_lines_list)==0:
                for bump in self.all_bump:
                    open_bump_list.append([bump])
                open_bump_list = self.remove_duplicate_sublists(open_bump_list)
                short_list = [-1] * len(open_bump_list)
                fault_bumps_list = [[short_lines, short_bumps, open_bump] for short_lines, short_bumps, open_bump in
                                    zip(short_list, short_list, open_bump_list)]
            else:
                for bump in self.all_bump:
                    for short_bumps, short_lines in zip(short_bumps_list, short_lines_list):
                        if bump not in short_bumps:
                            fault_bumps_list.append([short_lines, short_bumps, [bump]])
                            

        elif fault_type=='2open' or fault_type=='1short2open':
            if len(short_lines_list) == 0:
                for bump1 in self.all_bump:
                    for bump2 in self.all_bump:
                        if bump1!=bump2:
                            open_bump_list.append([bump1, bump2])
                open_bump_list = self.remove_duplicate_sublists(open_bump_list)
                short_list = [-1] * len(open_bump_list)
                fault_bumps_list = [[short_lines, short_bumps, open_bump] for short_lines, short_bumps, open_bump in
                                    zip(short_list, short_list, open_bump_list)]
            else:
                for bump1 in self.all_bump:
                    for bump2 in self.all_bump:
                        for short_bumps, short_lines in zip(short_bumps_list, short_lines_list):
                            if bump1 not in short_bumps and bump2 not in short_bumps and bump1!=bump2:
                                fault_bumps_list.append([short_lines, short_bumps, [bump1, bump2]])
        elif fault_type=='3open':
            if len(short_lines_list) == 0:
                for bump1 in self.all_bump:
                    for bump2 in self.all_bump:
                        for bump3 in self.all_bump:
                            if bump1!=bump2 and bump2!=bump3 and bump1!=bump3:
                                open_bump_list.append([bump1, bump2, bump3])
                open_bump_list = self.remove_duplicate_sublists(open_bump_list)
                short_list = [-1] * len(open_bump_list)
                fault_bumps_list = [[short_lines, short_bumps, open_bump] for short_lines, short_bumps, open_bump in
                                    zip(short_list, short_list, open_bump_list)]
        else:
            open_bumps_list = [-1] * len(short_lines_list)
            fault_bumps_list = [[short_lines, short_bumps, open_bump] for short_lines, short_bumps, open_bump in zip(short_lines_list, short_bumps_list, open_bumps_list)]

        return fault_bumps_list

    def construct_fault_bump(self, fault_bump_num=0, short_num=0, open_num=0):

        for type_name, value in faultType.items():
            if fault_bump_num != None:
                if int(value[0])==fault_bump_num:
                    print('\n===================================')
                    print(type_name)
                    short_lines_list = self.find_short_lines(type_name)
                    short_bumps_list = self.find_short_bumps(short_lines_list)
                    self.fault_bumps_list = self.find_open_given_short(type_name, short_lines_list, short_bumps_list)
                    print('number of possible fault:', len(self.fault_bumps_list),'\n')
                    self.construct_initial_score_list()
                    self.calculate_score()
            elif short_num!=None and open_num!=None:
                if int(value[1])==short_num and int(value[2])==open_num:
                    print('\n===================================')
                    print(type_name)
                    short_lines_list = self.find_short_lines(type_name)
                    short_bumps_list = self.find_short_bumps(short_lines_list)
                    self.fault_bumps_list = self.find_open_given_short(type_name, short_lines_list, short_bumps_list)
                    print('number of possible fault:', len(self.fault_bumps_list),'\n')
                    self.construct_initial_score_list()
                    self.calculate_score()
            elif short_num!=None:
                if int(value[1])==short_num and int(value[2])==0:
                    print('\n===================================')
                    print(type_name)
                    short_lines_list = self.find_short_lines(type_name)
                    short_bumps_list = self.find_short_bumps(short_lines_list)
                    self.fault_bumps_list = self.find_open_given_short(type_name, short_lines_list, short_bumps_list)
                    print('number of possible fault:', len(self.fault_bumps_list),'\n')
                    self.construct_initial_score_list()
                    self.calculate_score()
            elif open_num!=None:
                if int(value[2])==open_num:
                    print('\n===================================')
                    print(type_name)
                    #short_lines_list = self.find_short_lines(type_name)
                    #short_bumps_list = self.find_short_bumps(short_lines_list)
                    self.fault_bumps_list = self.find_open_given_short(type_name, short_lines_list=[], short_bumps_list=[])
                    print('number of possible fault:', len(self.fault_bumps_list),'\n')
                    self.construct_initial_score_list()
                    self.calculate_score()



    def construct_initial_score_list(self):
        # Find the maximum bundle number in the list of bumps
        max_bundle = max(bump.bundle for bump in self.all_bump)

        # Initialize the score list with zeros
        self.initial_score_list = [0] * (max_bundle + 1)
        self.bumps_per_bundle = [0] * (max_bundle + 1)

        # Calculate the initial score for each bundle
        for bump in self.all_bump:
            if bump.type == 3:  # Check if the bump is a spare
                self.initial_score_list[bump.bundle] += 1
            elif bump.type == 0:
                self.initial_score_list[0] += 1
            elif bump.type == 1:
                self.initial_score_list[1] += 1
            # Calculate the number of functional bump in each bundle
            else:               # the bump is a function
                self.bumps_per_bundle[bump.bundle] += 1

        print('Initial score for each bundle: ', self.initial_score_list)
        print('Number of functional bumps in each bundle: ', self.bumps_per_bundle)

    def check_need_repair(self, short_lines, short_bumps, open_bumps):
        if short_bumps!=-1 and (any(short_line.color=='red' for short_line in short_lines) or
                                any(short_line.color=='black' for short_line in short_lines) or
                                any(short_line.color=='fuchsia' for short_line in short_lines)):
            return True
        elif open_bumps!=-1 and any(open_bump.type==2 for open_bump in open_bumps):
            return True
        else:
            return False
    def calculate_score(self):
        pass_before_repair_count = 0
        pass_after_repair_count = 0
        catastrophic_num = 0
        for short_lines, short_bumps, open_bumps in self.fault_bumps_list:
            scores = copy.deepcopy(self.initial_score_list)
            need_to_repair = self.check_need_repair(short_lines, short_bumps, open_bumps)
            #print(len(short_lines), len(short_bumps))
            #for short_line in short_lines:
            #    print(str(short_line.color))
            #print(need_to_repair)
            Fail = False

            if short_lines!=-1 and any(short_line.color == 'red' for short_line in short_lines):
                Fail = True
                catastrophic_num +=1

            if not Fail and not need_to_repair:
                pass_before_repair_count += 1
                pass_after_repair_count += 1
            elif not Fail :
                if short_lines==-1:
                    for open_bump in open_bumps:
                        scores[open_bump.bundle] -= 1
                elif open_bumps==-1:
                    for short_bump in short_bumps:
                        scores[short_bump.bundle] -= 1
                    for short_line in short_lines:
                        if short_line.color=='orange' or short_line.color=='fuchsia':
                            (bump1, bump2) = short_line.link
                            if bump1.type == 0 or bump1.type == 1:  # Vss or Vdd
                                scores[bump2.bundle] += 1
                            else:
                                scores[bump1.bundle] += 1
                else:
                    for short_bump in short_bumps:
                        scores[short_bump.bundle] -= 1
                    for short_line in short_lines:
                        if short_line.color == 'orange' or short_line.color == 'fuchsia':
                            (bump1, bump2) = short_line.link
                            if bump1.type==0 or bump1.type==1: # Vss or Vdd
                                scores[bump2.bundle] += 1
                            else:
                                scores[bump1.bundle] += 1
                    for open_bump in open_bumps:
                        scores[open_bump.bundle] -= 1


                if all(value >= 0 for value in scores):
                    pass_after_repair_count += 1
                '''
                else:
                    print("Cannot repair score: ", scores)
                    for short_bump in short_bumps:
                        print("fault bump: ", short_bump.itemname, short_bump.id)
                        print("faulty bundle: ", short_bump.bundle )
                '''
        if len(self.fault_bumps_list)<=0:
            print("No faulty bumps")
        else:
            self.pass_after_repair = float(pass_after_repair_count/len(self.fault_bumps_list))
            self.pass_before_repair = float(pass_before_repair_count/len(self.fault_bumps_list))
        print('pass rate before repair: ', self.pass_before_repair, pass_before_repair_count, len(self.fault_bumps_list))
        print('pass rate after repair: ', self.pass_after_repair, pass_after_repair_count, len(self.fault_bumps_list))
        print('\nnumber of repairable faults: ', pass_after_repair_count-pass_before_repair_count)
        print('number of non-repairable faults: ', len(self.fault_bumps_list)-pass_after_repair_count)
        print('     number of catastrophic fault: ', catastrophic_num)
        print('     number of insufficient-spare fault: ', len(self.fault_bumps_list)-pass_after_repair_count-catastrophic_num)

class BumpInfo:
    def __init__(self, layout):

        self.larray = layout.construct_lmap()
        self.all_bump = layout.bump
        self.line_num = [0]*len(self.all_bump)

    def calculate_line_num(self):
        for line in self.larray:
            bump1, bump2 = line.link
            self.line_num[bump1.id]+=1
            self.line_num[bump2.id]+=1
        # print(self.line_num)


UCIeLayout = util.IArray()
dir = util.os.getcwd() + "\\.\\data\\"
layoutfilename = "\\UCIePitch51-55.csv"
listfilename = "\\test.csv"

# Parse layout form to a list form
parser = LayoutParser.layoutParser()
parser.read_csv(dir + layoutfilename)
parser.write_csv(dir + listfilename)

# Read layout from the list format file
UCIeLayout.read_csv(dir + listfilename)
# Construct micro-bump map
marray = UCIeLayout.construct_imap()


print('\n')
faultlist = FaultBumpsList(layout=UCIeLayout)
faultlist.construct_fault_bump(fault_bump_num=None, short_num=2, open_num=None)

bumpInfo = BumpInfo(layout=UCIeLayout)
bumpInfo.calculate_line_num()

