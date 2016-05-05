import sys
from ply import yacc
from lexer import lex, tokens

precedence = (
	('nonassoc', 'EQUALS', 'DIFFERENT'),
	('left', 'COMMA'),
	('left', 'CONCAT'),
	('left', 'OR', 'XOR'),
	('left', 'AND'),
	('right', 'NOT'),
	('nonassoc', 'LT', 'GT', 'LE', 'GE'),
	('left', 'PLUS', 'MINUS'),
	('left', 'TIMES', 'DIV'),
	('right', 'UNEG'),
)

class Node(object):
	"""Linked list class for string lists"""
	def __init__(self, data, next):
		self.data = data
		self.next = next

class Context(object):
	def __init__(self, output=sys.stdout):
		self.vars = {}
		self.out = output

class FakeOutput(object):
	def write(self, _):
		pass


def p_programT(p):
	'''
	program : TEXT
	'''
	text = p[1]
	def f(context):
		context.out.write(text)
	p[0] = f

def p_programB(p):
	'''
	program : block
	'''
	p[0] = p[1]

def p_programTI(p):
	'''
	program : TEXT program
	'''
	p_programT(p)
	first = p[0]
	rest = p[2]
	def f(context):
		first(context)
		rest(context)
	p[0] = f

def p_programBI(p):
	'''
	program : block program
	'''
	p_programB(p)
	first = p[0]
	rest = p[2]
	def f(context):
		first(context)
		rest(context)
	p[0] = f

def p_block(p):
	'''
	block : BEGIN stmt_list END
	'''
	p[0] = p[2]

def p_stmtB(p):
	'''
	stmt_list : stmt SEMICOLON
	'''
	p[0] = p[1]

def p_stmtI(p):
	'''
	stmt_list : stmt SEMICOLON stmt_list
	'''
	p_stmtB(p)
	first = p[0]
	rest = p[3]
	def f(context):
		first(context)
		rest(context)
	p[0] = f

def print_list(context, a):
	while a:
		context.out.write(a.data)
		a = a.next

def p_printE(p):
	'''
	stmt : PRINT expr
	'''
	arg = p[2]
	def f(context):
		a = arg(context)
		if isinstance(a, Node):
			print_list(context, a)
		else:
			context.out.write(str(a))
	p[0] = f

def p_printL(p):
	'''
	stmt : PRINT str_list
	'''
	arg = p[2]
	p[0] = lambda context: print_list(context, arg)

def p_exprPar(p):
	'''
	expr : LPAREN expr RPAREN
	'''
	p[0] = p[2]

def p_exprN(p):
	'''
	expr : MINUS INT %prec UNEG
	'''
	value = -p[2]
	p[0] = lambda _: value

def p_exprL(p):
	'''
	expr	: INT
			| STRING
	'''
	value = p[1]
	p[0] = lambda _: value

def p_exprB(p):
	'''
	expr	: TRUE
			| FALSE
	'''
	value = p[1] == "TRUE"
	p[0] = lambda _: value

def p_exprLN(p):
	'''
	expr : NOT expr
	'''
	value = p[2]
	def f(context):
		v = value(context)
		if type(v) == bool:
			return not v
		else:
			raise TypeError
	p[0] = f

def p_exprV(p):
	'''
	expr : IDENTIFIER
	'''
	variable = p[1]
	p[0] = lambda context: context.vars[variable]

def p_exprOps(p):
	'''
	expr	: expr PLUS expr
			| expr MINUS expr
			| expr TIMES expr
			| expr DIV expr
			| expr CONCAT expr
	'''
	left = p[1]
	op = {
		'+': lambda x,y: x+y,
		'-': lambda x,y: x-y,
		'*': lambda x,y: x*y,
		'/': lambda x,y: x/y,
		'.': lambda x,y: x+y,
	}[p[2]]
	right = p[3]
	def f(context):
		return op(left(context), right(context))
	p[0] = f

def p_exprComp(p):
	'''
	expr	: expr LT expr
			| expr LE expr
			| expr GT expr
			| expr GE expr
			| expr EQUALS expr
			| expr DIFFERENT expr
	'''
	left = p[1]
	op = {
		'<': lambda x,y: x<y,
		'>': lambda x,y: x>y,
		'>=': lambda x,y: x>=y,
		'<=': lambda x,y: x<=y,
		'=': lambda x,y: x==y,
		'!=': lambda x,y: x!=y,
	}[p[2]]
	right = p[3]
	def f(context):
		l = left(context)
		r = right(context)
		if type(l) == type(r):
			return op(l, r)
		else:
			raise TypeError
	p[0] = f

def p_exprBinLog(p):
	'''
	expr	: expr AND expr
			| expr OR expr
			| expr XOR expr
	'''
	left = p[1]
	op = {
		'AND': lambda x,y: x and y,
		'OR': lambda x,y: x or y,
		'XOR': lambda x,y: x ^ y,
	}[p[2]]
	right = p[3]
	def f(context):
		l = left(context)
		r = right(context)
		if type(l)==bool and type(r)==bool:
			return op(left(context), right(context))
		else:
			raise TypeError
	p[0] = f

def p_forL(p):
	'''
	stmt : FOR IDENTIFIER IN str_list DO stmt_list ENDFOR
	'''
	pass

def p_forV(p):
	'''
	stmt : FOR IDENTIFIER IN IDENTIFIER DO stmt_list ENDFOR
	'''
	pass

def p_it(p):
	'''
	stmt : IF expr DO stmt_list ENDIF
	'''
	cond = p[2]
	body = p[4]
	def f(context):
		if cond(context):
			body(context)
	p[0] = f

def p_ite(p):
	'''
	stmt : IF expr DO stmt_list ELSE stmt_list ENDIF
	'''
	cond = p[2]
	posbody = p[4]
	negbody = p[6]
	def f(context):
		if cond(context):
			posbody(context)
		else:
			negbody(context)
	p[0] = f

def p_assignE(p):
	'''
	stmt : IDENTIFIER ASSIGN expr
	'''
	lvalue = p[1]
	rvalue = p[3]
	def f(context):
		context.vars[lvalue] = rvalue(context)
	p[0] = f

def p_assignL(p):
	'''
	stmt : IDENTIFIER ASSIGN str_list
	'''
	lvalue = p[1]
	rvalue = p[3]
	def f(context):
		context.vars[lvalue] = rvalue
	p[0] = f

def p_stringListE(p):
	'''
	str_list : LPAREN RPAREN
	'''
	p[0] = None

def p_stringList1(p):
	'''
	str_list : LPAREN STRING COMMA RPAREN
	'''
	p[0] = Node(p[2], None)

def p_stringListM(p):
	'''
	str_list : LPAREN STRING COMMA strs RPAREN
	'''
	p[0] = Node(p[2], p[4])

def p_strsB(p):
	'''
	strs : STRING
	'''
	p[0] = Node(p[1], None)

def p_strsI(p):
	'''
	strs : STRING COMMA strs
	'''
	p[0] = Node(p[1], p[3])

def p_error(p):
	print "Syntax error near line", str(p.lineno)


yacc = yacc.yacc()
if __name__=="__main__":
	import sys
	inp = sys.stdin.read()
	context = Context(sys.stdout)
	yacc.parse(inp, debug=("-d" in sys.argv))(context)
