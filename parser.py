from ply import yacc
from lexer import lex, tokens

precedence = (
	('left', 'CONCAT'),
	('left', 'EQUALS'),
	('left', 'DIFFERENT'),
	('left', 'COMMA'),
)

def p_programB(p):
	'''
	program : TEXT
			| block
	'''
	p[0] = p[1]

def p_programI(p):
	'''
	program : TEXT program
			| block program
	'''
	#FIXME
	p[0] = p[1]

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
	#FIXME
	p[0] = p[1]

def p_print(p):
	'''
	stmt : PRINT str_expr
	'''
	pass

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
	pass

def p_ite(p):
	'''
	stmt : IF bool_expr DO stmt_list ELSE stmt_list ENDIF
	'''
	pass

def p_assignE(p):
	'''
	stmt : IDENTIFIER ASSIGN str_expr
	'''
	pass

def p_assignL(p):
	'''
	stmt : IDENTIFIER ASSIGN str_list
	'''
	pass

def p_stringL(p):
	'''
	str_expr : STRING
	'''
	p[0] = p[1]

def p_stringV(p):
	'''
	str_expr : IDENTIFIER
	'''
	#FIXME
	p[0] = p[1]

def p_boolL(p):
	'''
	bool_expr	: TRUE
				| FALSE
	'''
	p[0] = bool(p[1].lower())

def p_boolV(p):
	'''
	bool_expr : IDENTIFIER
	'''
	#FIXME
	p[0] = p[1]

def p_boolP(p):
	'''
	bool_expr : LPAREN bool_expr RPAREN
	'''
	#FIXME
	p[0] = p[1]

def p_boolE(p):
	'''
	bool_expr : bool_expr EQUALS bool_expr
	'''
	#FIXME
	p[0] = p[1]
	#TODO allow comparing string literals, for example

def p_boolNE(p):
	'''
	bool_expr : bool_expr DIFFERENT bool_expr
	'''
	#FIXME
	p[0] = p[1]

def p_concat(p):
	'''
	str_expr : str_expr CONCAT str_expr
	'''
	p[0] = p[1]+p[3]

def p_stringList(p):
	'''
	str_list : LPAREN strs RPAREN
	'''
	p[0] = p[2]

def p_strsB(p):
	'''
	strs : STRING
	'''
	p[0] = p[1]

def p_strsI(p):
	'''
	strs : strs COMMA strs
	'''
	#FIXME
	p[0] = p[1]

def p_error(p):
	print "Syntax error near line", str(p.lineno)
	yacc.error


yacc = yacc.yacc()
if __name__=="__main__":
	import sys
	inp = sys.stdin.read()
	print yacc.parse(inp)
