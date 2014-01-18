from ast import *
from varcheck import SymbolTable, VarCheck
from errors import Errors
import unittest

class SymbolTableTests(unittest.TestCase):
    
    def setUp(self):
        self.x = VariableDecl(int_type, 'x')
        self.x2 = VariableDecl(bool_type, 'x')
    
    def testEmpty(self):
        st = SymbolTable()
        self.assertEquals(st.get_names(), set())
        self.assertEquals(st.get_all_names(), set())
        self.assertIsNone(st.parent)

    def testEmptyWithParent(self):
        parent = SymbolTable()
        st = SymbolTable(parent)
        self.assertEquals(st.get_names(), set())
        self.assertEquals(st.get_all_names(), set())
        self.assertEquals(st.parent, parent)

    def testOneItem(self):
        st = SymbolTable()
        st.add('x', self.x, None)
        self.assertEquals(st.get_names(), set(['x']))
        self.assertEquals(st.get_all_names(), set(['x']))
        self.assertEquals(st.lookup('x'),  self.x)

    def testOneItemInParent(self):
        parent = SymbolTable()
        st = SymbolTable(parent)
        parent.add('x', self.x, None)
        self.assertEquals(st.get_names(), set())
        self.assertEquals(st.get_all_names(), set(['x']))
        self.assertEquals(st.lookup('x'), self.x)

    def testConflict(self):
        st = SymbolTable()
        errors = Errors()
        st.add('x', self.x, errors)
        st.add('x', self.x2, errors)
        self.assertEquals(errors.num_errors, 1)
        self.assertEquals(st.get_names(), set(['x']))
        self.assertEquals(st.lookup('x'), self.x)

    def testShadow(self):
        parent = SymbolTable()
        parent.add('x', self.x, None)
        st = SymbolTable(parent)
        errors = Errors()
        st.add('x', self.x2, errors)
        self.assertEquals(errors.num_warnings, 1)
        self.assertEquals(st.get_names(), set(['x']))
        self.assertEquals(st.get_all_names(), set(['x']))
        self.assertEquals(st.lookup('x'), self.x2)

    
class VarCheckTests(unittest.TestCase):

    def assertSuccess(self, input, expected_errors=0, expected_warnings=0):
        errors = Errors()
        vc = VarCheck(input, errors)
        self.assertEquals(errors.num_errors, expected_errors)
        self.assertEquals(errors.num_warnings, expected_warnings)

class VarCheckSymbolTableTests(VarCheckTests):

    def testEmpty(self):
        program = Program([])
        self.assertSuccess(program)
        self.assertEquals(program.symbol_table.get_names(), set())
        parent_table = program.symbol_table.parent
        for n in known_builtins.keys():
            self.assertTrue(n in parent_table.symbols)
        self.assertIsNone(parent_table.parent)

    def testVariableDecl(self):
        program = Program([VariableDecl(int_type, 'x')])
        self.assertSuccess(program)
        self.assertEquals(program.symbol_table.get_names(), set(['x']))

    def testFunctionDecl(self):
        program = Program([FunctionDecl(int_type, 'f', [], Block([]))])
        self.assertSuccess(program)
        self.assertEquals(program.symbol_table.get_names(), set(['f']))
        
    def testFunctionArgDecl(self):
        program = Program([FunctionDecl(int_type, 'f', [ArgDecl(int_type, 'x')], Block([]))])
        self.assertSuccess(program)
        self.assertEquals(program.symbol_table.get_names(), set(['f']))
        
        st = program.declarations[0].symbol_table
        self.assertEquals(st.get_names(), set(['x']))
        self.assertEquals(st.parent, program.symbol_table)
        
    def testFunctionBlock(self):
        block = Block([VariableDecl(int_type, 'x')])
        program = Program([FunctionDecl(int_type, 'f', [], block)])
        self.assertSuccess(program)
        
        st = block.symbol_table
        self.assertEquals(st.get_names(), set(['x']))
        self.assertEquals(st.get_all_names() - set(known_builtins.keys()), set(['f', 'x']))
        self.assertEquals(st.parent.parent, program.symbol_table)

class VarCheckVariableTests(VarCheckTests):

    def testGlobalVariable(self):
        d = VariableDecl(int_type, 'x')
        n = Name('x')
        block = Block([Statement(n)])
        program = Program([d, FunctionDecl(int_type, 'f', [], block)])
        self.assertSuccess(program)
        
        self.assertEquals(n.declaration, d)
    
    def testLocalVariable(self):
        d = VariableDecl(int_type, 'x')
        n = Name('x')
        block = Block([d, Statement(n)])
        program = Program([FunctionDecl(int_type, 'f', [], block)])
        self.assertSuccess(program)
        
        self.assertEquals(n.declaration, d)
    
    def testFunctionCall(self):
        g = FunctionDecl(int_type, 'g', [], Block([]))
        n = Name('g')
        block = Block([Statement(n)])
        program = Program([g, FunctionDecl(int_type, 'f', [], block)])
        self.assertSuccess(program)
        
        self.assertEquals(n.declaration, g)
    
    def testUndeclaredVariable(self):
        d = VariableDecl(int_type, 'x')
        n = Name('y')
        block = Block([d, Statement(n)])
        program = Program([FunctionDecl(int_type, 'f', [], block)])
        self.assertSuccess(program, expected_errors=1)
    
    def testUndeclaredFunction(self):
        n = Name('g')
        block = Block([Statement(FunctionCall(n, []))])
        program = Program([FunctionDecl(int_type, 'f', [], block)])
        self.assertSuccess(program, expected_errors=1)
    
    def testForwardFunctionCall(self):
        g = FunctionDecl(int_type, 'g', [], Block([]))
        n = Name('g')
        block = Block([Statement(n)])
        program = Program([FunctionDecl(int_type, 'f', [], block), g])
        self.assertSuccess(program, expected_errors=1)
        
        self.assertEquals(n.declaration, None)

if __name__ == '__main__':
    unittest.main()
