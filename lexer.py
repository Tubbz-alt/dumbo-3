import sys
from ply import lex

tokens = ['TEXT', 'BEGIN', 'END',
	'STRING', 'IDENTIFIER', 'CONCAT', 'SEMICOLON', 'ASSIGN',
	'LPAREN', 'RPAREN', 'COMMA',
	'EQUALS', 'DIFFERENT', 'LT', 'GT', 'LE', 'GE',
	'INT', 'PLUS', 'MINUS', 'TIMES', 'DIV']
keywords = ('PRINT', 'FOR', 'IN', 'DO', 'ENDFOR',
	'AND', 'OR', 'XOR', 'NOT',
	'LENGTHOF',
	'IF', 'ENDIF', 'ELSE', 'TRUE', 'FALSE')
tokens.extend(keywords) #idea from http://stackoverflow.com/a/5028233
states = (('code', 'exclusive'), )

def t_NEWLINE(t):
	r'\n+'
	t.lexer.lineno += len(t.value)
	#hack
	t.type = 'TEXT'
	return t
t_TEXT = r'[^{]+'
def t_BEGIN(t):
	'{{'
	t.lexer.begin('code')
	return t
def t_code_END(t):
	'}}'
	t.lexer.begin('INITIAL')
	return t
def t_error(t):
	#this should never run!
	assert(False)

t_code_ignore = ' \t'
def t_code_NEWLINE(t):
	r'\n+'
	t.lexer.lineno += len(t.value)
	pass
t_code_CONCAT = r'\.'
t_code_SEMICOLON = ';'
t_code_ASSIGN = ':='
t_code_EQUALS = '='
t_code_DIFFERENT = '!='
t_code_LPAREN = r'\('
t_code_RPAREN = r'\)'
t_code_COMMA = ','
t_code_PLUS = r'\+'
t_code_MINUS = '-'
t_code_TIMES = r'\*'
t_code_DIV = r'/'
t_code_LT = '<'
t_code_GT = '>'
t_code_LE = '<='
t_code_GE = '>='
def t_code_IDENTIFIER(t):
	'[a-zA-Z_][a-zA-Z0-9_]*'
	u = t.value.upper()
	if u in keywords:
		t.type = t.value = u
	return t
def t_code_INT(t):
	'[0-9]+'
	t.value = int(t.value)
	return t
def t_code_STRING(t):
	r"'([^'\n]|\\')*'"
	t.value = t.value[1:-1].replace(r"\'", "'")
	#TODO regex replace for at least unescaped \n and \t
	return t
def t_code_error(t):
	where = "at line "+str(t.lexer.lineno)
	if t.value[0] == "'":
		print >>sys.stdout, "Unterminated string literal", where
	else:
		print >>sys.stdout, "Illegal character", repr(t.value[0]), where
	t.lexer.skip(1)

lex = lex.lex()
if __name__=="__main__":
	lex.input(sys.stdin.read())
	for token in lex:
		print token.type
