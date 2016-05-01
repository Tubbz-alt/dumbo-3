import sys
from ply import yacc
from lexer import lex, tokens

precedence = (
	('left', 'CONCAT'),
	('left', 'EQUALS'),
	('left', 'DIFFERENT'),
	('left', 'COMMA'),
)

class Node(object):
	def __init__(self, data, next):
		self.data = data
		self.next = next

def p_programT(p):
	'''
	program : TEXT
	'''
	def f(context):
		sys.stdout.write(p[1])
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
	def f(context):
		first(context)
		p[2](context)
	p[0] = f

def p_programBI(p):
	'''
	program : block program
	'''
	p_programB(p)
	first = p[0]
	def f(context):
		first(context)
		p[2](context)
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
	p[0] = lambda _: Node(p[1], None)

def p_stmtI(p):
	'''
	stmt_list : stmt SEMICOLON stmt_list
	'''
	p[0] = lambda _: Node(p[1], p[3])

def p_print(p):
	'''
	stmt : PRINT str_expr
	'''
	def f(context):
		sys.stdout.write(p[2](context))
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
	stmt : IF bool_expr DO stmt_list ENDIF
	'''
	def f(context):
		if p[2](context):
			p[4](context)
	p[0] = f

def p_ite(p):
	'''
	stmt : IF bool_expr DO stmt_list ELSE stmt_list ENDIF
	'''
	def f(context):
		if p[2](context):
			p[4](context)
		else:
			p[6](context)
	p[0] = f

def p_assignE(p):
	'''
	stmt	: IDENTIFIER ASSIGN str_expr
			| IDENTIFIER ASSIGN str_list
	'''
	def f(context):
		context[p[1]] = p[3](context)
	p[0] = f

def p_stringL(p):
	'''
	str_expr : STRING
	'''
	p[0] = lambda _: p[1]

def p_stringV(p):
	'''
	str_expr : IDENTIFIER
	'''
	p[0] = lambda context: context[p[1]]

def p_boolL(p):
	'''
	bool_expr	: TRUE
				| FALSE
	'''
	p[0] = lambda _: bool(p[1].lower())

def p_boolV(p):
	'''
	bool_expr : IDENTIFIER
	'''
	p[0] = lambda context: context[p[1]]

def p_boolP(p):
	'''
	bool_expr : LPAREN bool_expr RPAREN
	'''
	p[0] = p[1]

def p_boolE(p):
	'''
	bool_expr : bool_expr EQUALS bool_expr
	'''
	p[0] = lambda context: p[1](context) == p[3](context)
	#TODO allow comparing string literals, for example

def p_boolNE(p):
	'''
	bool_expr : bool_expr DIFFERENT bool_expr
	'''
	p[0] = lambda context: p[1](context) != p[3](context)

def p_concat(p):
	'''
	str_expr : str_expr CONCAT str_expr
	'''
	p[0] = lambda context: p[1](context)+p[3](context)

def p_stringList(p):
	'''
	str_list : LPAREN strs RPAREN
	'''
	p[0] = p[2]

def p_strsB(p):
	'''
	strs : STRING
	'''
	p[0] = Node(lambda _: p[1], None)

def p_strsI(p):
	'''
	strs : STRING COMMA strs
	'''
	p_strsB(p)
	first = p[0]
	p[0] = Node(lambda _: first, p[3])

def p_error(p):
	print "Syntax error near line", str(p.lineno)
	yacc.error


yacc = yacc.yacc()
if __name__=="__main__":
	import sys
	inp = sys.stdin.read()
	yacc.parse(inp)({})
