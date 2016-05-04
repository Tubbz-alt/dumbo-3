import sys
from ply import yacc
from lexer import lex, tokens

precedence = (
	('nonassoc', 'EQUALS', 'DIFFERENT', 'LT', 'GT', 'LE', 'GE'),
	('left', 'COMMA'),
	('left', 'CONCAT'),
	('left', 'PLUS', 'MINUS'),
	('left', 'TIMES', 'DIV'),
)

class Node(object):
	"""Linked list class for string lists"""
	def __init__(self, data, next):
		self.data = data
		self.next = next

def p_programT(p):
	'''
	program : TEXT
	'''
	text = p[1]
	def f(context):
		sys.stdout.write(text)
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

def p_print(p):
	'''
	stmt	: PRINT expr
			| PRINT str_list
	'''
	arg = p[2]
	def f(context):
		sys.stdout.write(arg(context))
	p[0] = f

def p_exprPar(p):
	'''
	expr : LPAREN expr RPAREN
	'''
	p[0] = p[2]

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
	value = bool(p[1].lower())
	p[0] = lambda _: value

def p_exprV(p):
	'''
	expr : IDENTIFIER
	'''
	variable = p[1]
	p[0] = lambda context: context[variable]

def p_exprBin(p):
	'''
	expr : expr binop expr
	'''
	left = p[1]
	op = p[2]
	right = p[3]
	p[0] = lambda context: op(left(context), right(context))

def p_binop(p):
	'''
	binop	: LT
			| GT
			| LE
			| GE
			| EQUALS
			| DIFFERENT
			| PLUS
			| MINUS
			| TIMES
			| DIV
	'''
	o = {
		'<': lambda x,y: x<y,
		'>': lambda x,y: x>y,
		'>=': lambda x,y: x>=y,
		'<=': lambda x,y: x<=y,
		'=': lambda x,y: x==y,
		'!=': lambda x,y: x!=y,
		'+': lambda x,y: x+y,
		'-': lambda x,y: x-y,
		'*': lambda x,y: x*y,
		'/': lambda x,y: x/y,
	}
	return o[p]

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
	stmt	: IDENTIFIER ASSIGN str_expr
			| IDENTIFIER ASSIGN str_list
	'''
	lvalue = p[1]
	rvalue = p[3]
	def f(context):
		context[lvalue] = rvalue(context)
	p[0] = f

def p_stringL(p):
	'''
	str_expr : STRING
	'''
	s = p[1]
	p[0] = lambda _: s

def p_concat(p):
	'''
	str_expr : str_expr CONCAT str_expr
	'''
	first = p[1]
	second = p[3]
	p[0] = lambda context: first(context) + second(context)

def p_stringList(p):
	'''
	str_list	: LPAREN STRING COMMA strs RPAREN
				| LPAREN STRING COMMA RPAREN
				| LPAREN RPAREN
	'''
	p[0] = lambda _: '42'

def p_strsB(p):
	'''
	strs : STRING
	'''
	s = p[1]
	p[0] = Node(lambda _: s, None)

def p_strsI(p):
	'''
	strs : STRING COMMA strs
	'''
	p_strsB(p)
	first = p[0]
	p[0] = Node(lambda _: first, p[3])

def p_error(p):
	print "Syntax error near line", str(p.lineno)


yacc = yacc.yacc()
if __name__=="__main__":
	import sys
	inp = sys.stdin.read()
	yacc.parse(inp)({})
