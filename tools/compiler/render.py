from utils import expect
from utils.visitor import Visitor
from compiler.phase import Phase
from compiler.ast import *
from compiler.linearise import Entry


class Render(Phase, Visitor):
    def __init__(self, lines, machine, indent=True, **kwargs):
        super(Render, self).__init__(**kwargs)
        self.lines = lines
        self.machine = machine
        self.indent = indent
    
    def run_phase(self):
        self.output = []
        self.visit(self.lines)
        return self.output
    
    def visit_Label(self, label):
        line = '%s:' % label.name
        if label.public:
            line = line + ':'
        if isinstance(label.node, Entry) and len(self.output) > 0:
            self.add_line('')
        self.add_line(line)

    def visit_Branch(self, branch):
        arg = self.render(branch.expression)
        line = 'br %s, %s' % (arg, branch.target)
        self.add_line(line, indent=1)

    def visit_Jump(self, jump):
        line = 'jmp %s' % jump.target
        self.add_line(line, indent=1)

    def visit_Instruction(self, instr):
        self.visit_parts(instr)

    def visit_AssignStatement(self, assign):
        if  isinstance(assign.expression, Numeral):
            dest = self.render(assign.target)
            line = 'mov %d, %s' % (assign.expression.value, dest)
        elif isinstance(assign.expression, Name):
            if isinstance(assign.target, Name):
                if assign.target.declaration.register == assign.expression.declaration.register:
                    return
            dest = self.render(assign.target)
            src = self.render(assign.expression)
            line = 'mov %s, %s' % (src, dest)
        elif isinstance(assign.expression, BinaryOperation):
            dest = self.render(assign.target)
            arg1 = self.render(assign.expression.parts[0])
            arg2 = self.render(assign.expression.parts[2])
            opr = assign.expression.parts[1]
            if opr == '<':
                line = 'slt %s, %s, %s' % (arg1, arg2, dest)
            elif opr == '+':
                line = 'add %s, %s, %s' % (arg1, arg2, dest)
            elif opr == '-':
                line = 'sub %s, %s, %s' % (arg1, arg2, dest)
            else:
                line = '%s %s, %s, %s' % (opr, arg1, arg2, dest)
                #raise NotImplementedError(repr(op))
        else:
            #raise NotImplementedError(repr(op))
            line = '%s' % assign
        self.add_line(line, indent=1)

    def visit_FunctionCall(self, fc):
        if isinstance(fc.name.declaration, Builtin):
            line = self.machine.render(fc, [self.render(x) for x in fc.args])
        else:
            #raise NotImplementedError(fc)
            line = '%s' % fc
        self.add_line(line, indent=1)

    def add_line(self, line, indent=0):
        if self.indent:
            line = '    ' * indent + line
        self.output.append(line)

    @expect.input(Expression)
    def render(self, expr):
        if isinstance(expr, Numeral):
            return str(expr.value)
        elif isinstance(expr, Name):
            decl = expr.declaration
            if isinstance(decl, Register):
                return decl.name
            else:
                return decl.register.name
        else:
            raise NotImplementedError(repr(expr))
