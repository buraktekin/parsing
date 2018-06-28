from collections import defaultdict

class CNF(object):
    """
    !! IMPORTANT NOTE !!:
    This part will be referenced in comments in the code base below. While referencing the symbol
    '@' will be in use.
    
    Rules to follow for chomsky normal form conversion are as follows:
    1. Define a start symbol. If there is Start Symbol on the right hand side (RHS), create 
    a new rule which derives Start Symbol (S).
    2. Get rid of ε-productions if any exists.
    3. Get rid of all productions with one non-terminal symbol on the RHS.
    4. Replace all long productions (which has more than 2 symbols) with the shorter ones.
    5. Move all terminals to productions.
    """

    def __init__(self):
        #-----------------------------------------------
        # CONSTANTS:
        self.EPSILON = "ε"
        self.start_symbol = None
        self.filename = "grammar.txt"
        self.non_terminals = list()
        #-----------------------------------------------
        
        #-----------------------------------------------
        # RULES: this turns all productions into a list 
        # and if there is no available key then this 
        # returns an empty list
        self.rules = defaultdict(list)
        #-----------------------------------------------
        
        #-----------------------------------------------
        # Load Grammar from text file...
        self.load_grammar("./grammar.txt")
        self._eliminate_epsilon_productions()
        self._eliminate_unit_productions()
        print(self.rules)
        #-----------------------------------------------

    def define_start_symbol(self, symbol):
        self.start_symbol = symbol
    
    def load_grammar(self, filename):
        self.filename = filename
        with open(self.filename, "r") as grammar:
            rules = grammar.readlines()
            for rule in rules:
                #-----------------------------------------------
                # Split lhs and rhs of the rules to
                # create a dictionary of rules
                lhs, rhs = rule.strip().split(" -> ")
                self.non_terminals.append(lhs)
                rhs_symbols = rhs.strip().split(" | ")
                if rules.index(rule) == 0:
                    self.start_symbol = lhs
                for r in rhs_symbols:
                    self.rules[lhs].append(r.split())
                #-----------------------------------------------
                
                #-----------------------------------------------
                # Check start symbol: Rule @1
                self.check_start_symbol_on_rhs(
                    self.start_symbol, 
                    rhs_symbols
                )
                #-----------------------------------------------
        return self.rules

    def check_start_symbol_on_rhs(self, symbol, rhs):
        #-----------------------------------------------
        ''' If RHS carries the start symbol generate a new rule '''
        if symbol in rhs:
            new_symbol = symbol + "'"
            self.rules[new_symbol].append([symbol])
            self.start_symbol = new_symbol
        #-----------------------------------------------

    def find_epsilon_productions(self):
        for lhs in self.rules:
            if not self.start_symbol is None and lhs == self.start_symbol:
                continue
            for index, rhs in enumerate(self.rules[lhs]):
                if self.EPSILON in rhs:
                    return lhs, index # EPSILON found in index 'index'

        return None, None

    def _eliminate_epsilon_productions(self):
        while True:
            # Get the production rules have EPSILON in it.
            lhs, index = self.find_epsilon_productions()
            
            #-----------------------------------------------
            # NOTE:
            # if find_epsilon_productions returns nothing 
            # for LHS then break the loop.
            if lhs is None:
                break
            #-----------------------------------------------
            
            #-----------------------------------------------
            # Delete epsilon rule from RHS
            del self.rules[lhs][index]
            #-----------------------------------------------

            # Create the new productions for the rules that 
            # contains the LHS non-terminals which has 
            # EPSILON rule.
            for symbol in self.rules:
                no_epsilon = list()
                for possible_lhs_of_rule in self.rules[symbol]:
                    number_of_epsilon_carrier = possible_lhs_of_rule.count(lhs)
                    if (number_of_epsilon_carrier == 0) & (possible_lhs_of_rule not in no_epsilon):
                        no_epsilon.append(possible_lhs_of_rule)
                    else:
                        new_productions = self._create_new_productions(
                                rule = possible_lhs_of_rule,
                                lhs = lhs,
                                number_of_epsilon = number_of_epsilon_carrier
                            )
                        if new_productions not in no_epsilon:
                            no_epsilon.extend(new_productions)

                self.rules[symbol] = no_epsilon

    def _create_new_productions(self, rule, lhs, number_of_epsilon):
        ''' 
            NOTE:
            ( !! VERY CHALLENGING !! POSSIBLY NEED A REFACTORING )
            Lets say we have rules like B -> ... | ε and S -> BS then
            the following productions should be generated:
                S -> BS | S
                    |- 2 new productions -|

            2. if B -> ... | ε and S -> BSB then
                S -> BSB | BS | SB | S
                    |- 4 new productions -|
            
            3. if B -> ... | ε and S -> BSBSB then
                S -> BSBSB | SBSB | BSSB | BSBS | SSB | BSS | SBS | SS
                    |---------------- 8 new productions --------------|

            ... and so on.

            As you can see the number of new productions changes by the nth 
            power of 2 where n is the number of non-terminals which has ε production.
            So, while we creating new productions we would create 2^n new productions
            for the production carrying ε production and replace that production with
            the output.
        '''

        number_of_productions = 2 ** number_of_epsilon
        list_of_new_productions = []

        for i in range(number_of_productions):
            nth_nt = 0
            new_production = []
            for s in rule:
                if s == lhs:
                    if i & (2 ** nth_nt):
                        new_production.append(s)
                    nth_nt += 1
                else:
                    new_production.append(s)
            if len(new_production) == 0:
                new_production.append(self.EPSILON)
            list_of_new_productions.append(new_production)
        return list_of_new_productions

    def _eliminate_unit_productions(self):
        for lhs in self.rules:
            for index, rhs in enumerate(self.rules[lhs]):
                terminals = [symbol for symbol in rhs if symbol not in self.non_terminals]
                print("Terminals: ", terminals)
                if(len(rhs) == 1):
                    print(self.non_terminals, rhs)


if __name__ == '__main__':
    CNF()