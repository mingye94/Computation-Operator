import doctest
import ast
from collections import OrderedDict

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.

class Symbol:
    # overrde the existing operation and reverse operation method for each symbolic expression for python integration
    def __radd__(self, other):
        return Add(other, self)
    
    def __add__(self, other):
        return Add(self, other)
    
    def __rsub__(self, other):
        return Sub(other, self)
    
    def __sub__(self, other):
        return Sub(self, other)
    
    def __rmul__(self, other):
        return Mul(other, self)
    
    def __mul__(self, other):
        return Mul(self, other)
    
    def __rtruediv__(self, other):
        return Div(other, self)
    
    def __truediv__(self, other):
        return Div(self, other)


class BinOp(Symbol):
    def __init__(self, left, right):
        # if the input is int or str, build up instance of Num or Var
        if isinstance(left, int):
            self.left = Num(left)
        elif isinstance(left, str):
            self.left = Var(left)
        else:
            self.left = left
            
        if isinstance(right, int):
            self.right = Num(right)
        elif isinstance(right, str):
            self.right = Var(right)
        else:
            self.right = right

    
    # similar as repr for the Num and Var class
    def __repr__(self):
        return self.__class__.__name__ + '(' + repr(self.left) + ', ' + repr(self.right) + ')'
    
    # similar as str for Num and Var class except the parenthesis thing; need to wrap the string of expression with parenthesis 
    # during the certain cases shown in the instruction
    def __str__(self):
        if self.pre > self.left.pre:
            if self.pre > self.right.pre:
                return '(' + str(self.left) + ')' + ' ' + self.operand + ' ' + '(' + str(self.right) + ')'
            
            elif self.special(self.right):
                return '(' + str(self.left) + ')' + ' ' + self.operand + ' ' + '(' + str(self.right) + ')'
            else:
                return '(' + str(self.left) + ')' + ' ' + self.operand + ' ' + str(self.right)
            
        else:
            if self.special(self.right):
                return str(self.left) + ' ' + self.operand + ' ' + '(' + str(self.right) + ')'
            elif self.pre > self.right.pre:
                return str(self.left) + ' ' + self.operand + ' ' + '(' + str(self.right) + ')'
            else:
                return str(self.left) + ' ' + self.operand + ' ' + str(self.right)
    
        
class Add(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        # set up the operand for the add class
        self.pre = 1
        self.operand = '+'
            
    def special(self, other):
        return False
        
    def simplify(self):
        # try to simplify each part first
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        
        # for the simplified version, determine if it can be further simplified, if yes, simplify it and return the simplified version
        # if not, return it
        if isinstance(self.left, Num) and isinstance(self.right, Num):
            return Num(self.left.n + self.right.n)
        if isinstance(self.left, Num) and not isinstance(self.right, Num):
            if self.left.n == 0:
                return self.right
        if not isinstance(self.left, Num) and isinstance(self.right, Num):
            if self.right.n == 0:
                return self.left
        return self
    def eval(self, d_para):
        self.left = self.left.eval(d_para)
        self.right = self.right.eval(d_para)
        return self.left + self.right
    
    def deriv(self, param):
        left_op = self.left.deriv(param)
        right_op = self.right.deriv(param)
        return Add(left_op, right_op)
    
# similar as the add class
class Sub(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.pre = 1
        self.operand = '-'
            
    def special(self, other):
        if self.pre == other.pre:
            return True
        else:
            return False
    
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()

        if isinstance(self.left, Num) and isinstance(self.right, Num):
            return Num(self.left.n - self.right.n)
        if not isinstance(self.left, Num) and isinstance(self.right, Num):
            if self.right.n == 0:
                return self.left
        return self
    def eval(self, d_para):
        self.left = self.left.eval(d_para)
        self.right = self.right.eval(d_para)
        return self.left - self.right
    
    def deriv(self, param):
        left_op = self.left.deriv(param)
        right_op = self.right.deriv(param)
        return Sub(left_op, right_op)
    
# similar as the add class        
class Mul(BinOp):       
    def __init__(self, left, right):
        super().__init__(left, right)
        self.pre = 2
        self.operand = '*'
            
    def special(self, other):
        return False
    
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        
        if isinstance(self.left, Num) and isinstance(self.right, Num):
            return Num(self.left.n * self.right.n)
        if isinstance(self.left, Num):
            if self.left.n == 0:
                return Num(0)
            if self.left.n == 1:
                return self.right
        if isinstance(self.right, Num):
            if self.right.n == 0:
                return Num(0)
            if self.right.n == 1:
                return self.left
        return self
    
    def eval(self, d_para):
        self.left = self.left.eval(d_para)
        self.right = self.right.eval(d_para)
        return self.left * self.right
    
    def deriv(self, param):
        left_op = Mul(self.left, self.right.deriv(param))
        right_op = Mul(self.right, self.left.deriv(param))
        return Add(left_op, right_op)
    
# similar as the add class
class Div(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.pre = 2
        self.operand = '/'
            
    def special(self, other):
        if self.pre == other.pre:
            return True
        else:
            return False
        
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
    
        if isinstance(self.left, Num) and isinstance(self.right, Num):
            return Num(self.left.n / self.right.n)
        if isinstance(self.left, Num) and not isinstance(self.right, Num):
            if self.left.n == 0:
                return Num(0)
        if not isinstance(self.left, Num) and isinstance(self.right, Num):
            if self.right.n == 1:
                return self.left
        return self
    
    def eval(self, d_para):
        self.left = self.left.eval(d_para)
        self.right = self.right.eval(d_para)
        return self.left / self.right
    
    def deriv(self, param):
        left_op = Mul(self.right, self.left.deriv(param))
        right_op = Mul(self.left, self.right.deriv(param))
        top_part = Sub(left_op, right_op)
        bottom_part = Mul(self.right, self.right)
        return Div(top_part, bottom_part)
    
class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n
        self.pre = 3
        
    def special(self, other):
        return False
    # the derivative of a variable can be divided into two cases; if it is same as the parameter respect to which we are differetiating.
    # it is equal to 1; if it is different from the parameter, it is equal to 0
    def deriv(self, param):
        if self.name == param:
            return Num(1)
        else:
            return Num(0)
    
    # return itself if the symbolic expression is an instance of Var
    def simplify(self):
        return self
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Var(' + repr(self.name) + ')'
    
    def eval(self, d_para):
        return d_para[str(self)]
        
class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n
        self.pre = 3
        
    def special(self, other):
        return False
    
    # the derivative of a constant number is 0
    def deriv(self, param):
        return Num(0)
    
    # return itself if the symbolic expression is an instance of Num
    def simplify(self):
        return self
    
    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return 'Num(' + repr(self.n) + ')'
    
    def eval(self, d_para):
        return self.n
    
def tokenize(input_str):
    num = ''
    output = []
    
    if input_str.isdigit() or input_str.isalpha():
        return [input_str]
            
    for i in range(len(input_str)):
#        print(output)
#        print(input_str[i])
        if input_str[i] == '-':
            if input_str[i+1].isdigit():
                num += input_str[i]
            else:
                output.append(input_str[i])
                
        elif input_str[i].isdigit():
            num += input_str[i]
        elif input_str[i] == ' ' and num != '':
            output.append(num)
#            print(output)
            num = ''
        elif input_str[i] == ' ' and num == '':
            continue
        elif input_str[i] == ')' and num != '':
            output.append(num)
            num = ''
            output.append(input_str[i])
#        elif input_str[i] == ')' and num == '':
#            output.append(input_str[i])
        else:
            output.append(input_str[i])
            
    if num != '':
        output.append(num)
    return output

def precedence(a, b):
    if a == '*' or a == '/':
        if b == '+' or b == '-' or b == '(':
            return 'high'
        else:
            return 'equal'
        
    if a == '+' or a == '-':
        if b == '+' or b == '-':
            return 'equal'
        elif b == '*' or b == '/':
            return 'low'
        else:
            return 'high'
        
def parse(token_list):
   '''((1 + 3) - 2)'''
   num = []
   operator = []
   if len(token_list) == 1:
       if token_list[0].isdigit():
           return Num(int(token_list[0]))
       if token_list[0].isalpha():
           if token_list[0] == 'quit':
               return 'End'
           else:
               return Var(token_list[0])
       
   for i in token_list:
       if i.isdigit():
           num.append(Num(int(i)))
       elif i.isalpha():
           num.append(Var(i))
           
       elif i[0] == '-' and i[1:].isdigit():
           num.append(Num(-int(i[1:])))
         
       elif i == ')':
           right_op = num.pop()
           left_op = num.pop()
           op = operator.pop()
           operator.pop()
           if op == '*':
               num.append(Mul(left_op, right_op))
           elif op == '/':
               num.append(Div(left_op, right_op))
           elif op == '+':
               num.append(Add(left_op, right_op))
           else:
               num.append(Sub(left_op, right_op))
                   
       elif i == '(':
           operator.append(i)
       else:
           if precedence (i, operator[-1]) == 'low' or precedence (i, operator[-1]) == 'equal':
               right_op = num.pop()
               left_op = num.pop()
               op = operator.pop()
               if op == '*':
                   num.append(Mul(left_op, right_op))
               elif op == '/':
                   num.append(Div(left_op, right_op))
               elif op == '+':
                   num.append(Add(left_op, right_op))
               else:
                   num.append(Sub(left_op, right_op))
           else:
               operator.append(i)
        
   return num[-1]

def sym(input_str):
    token_list = tokenize(input_str)
    return parse(token_list)
   
if __name__ == '__main__':
    # for repl test
    # accept the str input
    input_str = ''
    while input_str != 'quit':
        input_str = input('enter the string you want: ')
        token_list = tokenize(input_str)
        try:
            result = parse(token_list)
            print(repr(result))
        except Exception as e:
            print(e)
    #print(tokenize('quit')) 