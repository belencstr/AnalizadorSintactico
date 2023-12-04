from lark import Lark, Transformer, v_args
from anytree import Node, RenderTree
from graphviz import Digraph


# Define la gramática en forma de string
calculator_grammar = """
    start: operation

    ?operation: assign
                | function
                | expression
    
    ?assign: var "=" expression

    ?function: func "(" expression ")"

    ?expression: sum
        | expression "+" sum   -> add
        | expression "-" sum   -> sub
    
    ?sum: product
        | sum "*" product  -> mul
        | sum "/" product  -> div

    ?product: atom
        | product "^" atom  -> pow

    ?atom: NUMBER           -> number
            | "-" atom         -> neg
            | "(" expression ")"
        
    ?var: CNAME             -> var
     
    ?func: CNAME            -> func


    %import common.CNAME
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

# Define el parser con la gramática
parser = Lark(calculator_grammar, start="start", parser="lalr", transformer=Transformer())

# Define el Transformer para construir el AST
@v_args(inline=True)
class TreeBuilder(Transformer):
    def add(self, x, y):
        return Node('+', children=[x, y])

    def sub(self, x, y):
        return Node('-', children=[x, y])

    def mul(self, x, y):
        return Node('*', children=[x, y])

    def div(self, x, y):
        return Node('/', children=[x, y])

    def number(self, value):
        return Node(f'Number: {value}')

    def neg(self, value):
        return Node('-', children=[value])

    def var(self, value):
        return Node(f'Variable: {value}')

    def func(self, value ):
        return Node(f'Function: {value}')

    def assign(self, x, y):
        return Node('assign', children=[x, y])

    def function(self, x, y):
        return Node('function', children=[x, y])

    def pow(self, x, y):
        return Node('^', children=[x, y])

    def start(self, x):
        return x


# Función para analizar una expresión y obtener el AST
def parse_expression(expr):
    tree = parser.parse(expr)
    ast = TreeBuilder().transform(tree)
    return ast

def generate_graph(tree):
    dot = Digraph(comment='Abstract Syntax Tree')
    add_nodes(dot, tree)
    return dot

def add_nodes(dot, node):
    dot.node(str(id(node)), node.name)
    for child in node.children:
        dot.edge(str(id(node)), str(id(child)))
        add_nodes(dot, child)

# Ejemplo de uso
expression = "2^2 * (-3 + 4) - ((5 * 7) / 2) / (2 - 3)"
ast = parse_expression(expression)

# Generar el gráfico del árbol sintáctico
graph = generate_graph(ast)
graph.render("ast_graph", format="png", view=True)
