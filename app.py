from contextlib import nullcontext
from urllib import request


from flask import Flask, jsonify, request, render_template
from unicodedata import digit

app = Flask(__name__)


class Token:
    def __init__(self, token_type, value=None):
        self.type = token_type
        self.value = value


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None
        if self.current_char == '\n':  # Skip over newline characters
            self.advance()

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        else:
            return None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # implement
    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
        return (float(result), 1) if '.' in result else (int(result), 0)

    # implement
    def identifier(self):
        ident = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            ident += self.current_char
            self.advance()
        return ident

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            elif self.current_char.isdigit():
                res = self.number()
                if res[1] == 1:
                    return Token('FNUMBER', res[0])
                else:
                    return Token('NUMBER', res[0])
            elif self.current_char.isalpha() or self.current_char == '_':
                return self.keyword_or_identifier()
            elif self.current_char == '+' or self.current_char == '-' or self.current_char == '*' or self.current_char == '/':
                return self.operator()
            elif self.current_char == '(' or self.current_char == ')':
                token = Token('PARENTHESIS', self.current_char)
                self.advance()
                return token
            elif self.current_char == '{' or self.current_char == '}':
                token = Token('SCOPE', self.current_char)
                self.advance()
                return token
            elif self.current_char == '\n':  # Change delimiter to newline character
                token = Token('DELIMITER', self.current_char)
                self.advance()
                return token
            elif self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('OPERATOR', '!=')
                else:
                    self.error()

            elif self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('OPERATOR', '==')
                else:
                    return Token('OPERATOR', '=')

            elif self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('OPERATOR', '<=')
                else:
                    return Token('OPERATOR', '<')
            elif self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('OPERATOR', '>=')
                else:
                    return Token('OPERATOR', '>')
            else:
                self.error()
        return Token('EOF')

    # implement
    def keyword_or_identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        keywords = {'int', 'float', 'if', 'else', 'while', 'do', 'then'}
        if result in keywords:
            return Token('KEYWORD', result)
        return Token('IDENTIFIER', result)

    # implement
    def operator(self):
        operator = self.current_char
        self.advance()
        return Token('OPERATOR', operator)



class Node:
    pass


class ProgramNode(Node):
    def __init__(self, statements):
        self.statements = statements


class DeclarationNode(Node):
    def __init__(self, identifier, expression, myType):
        self.identifier = identifier
        self.expression = expression
        self.type = myType


class AssignmentNode(Node):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression


class IfStatementNode(Node):
    def __init__(self, condition, if_block, else_block):
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block


class WhileLoopNode(Node):
    def __init__(self, condition, loop_block):
        self.condition = condition
        self.loop_block = loop_block


class ConditionNode(Node):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class ArithmeticExpressionNode(Node):
    def __init__(self, operator, left, right, myType):
        self.operator = operator
        self.left = left
        self.right = right
        self.type = myType


class TermNode(Node):
    def __init__(self, operator, left, right, myType):
        self.operator = operator
        self.left = left
        self.right = right
        self.type = myType


class FactorNode(Node):
    def __init__(self, value, myType):
        self.value = value
        self.type = myType


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        # implement symbol table and scopes

        self.messages = []
        self.scopes = []


    def error(self, message):
        self.messages.append(message)


    def eat(self, token_type):
        if self.current_token.type == token_type:
            print(f'Eating token(last): {self.current_token.value}')
            self.current_token = self.lexer.get_next_token()
            print(f'Current token: {self.current_token.value}')
        else:
            print(f'Expected token of type {token_type}, but found {self.current_token.type}')

        # enter the new scope in the program


    def enter_scope(self, scope_prefix):
        self.scope = {"scope_prefix": scope_prefix, "variable": {}}
        self.scopes.append(self.scope)
        # leave the current scope


    def leave_scope(self):
        if self.scopes:
            self.scopes.pop()
        # return the current scope


    def current_scope(self):
        return self.scopes[-1]


    def checkVarNotDeclared(self, identifier):
        if identifier in self.current_scope()["variable"]:
            self.error(f'Variable {identifier} has already been declared in the current scope')
            return False
        return True


    def checkVarUse(self, identifier):
        for scope in reversed(self.scopes):
            if identifier in scope["variable"]:
                return True
        if identifier in self.scopes[0]["variable"]:
            return True
        self.error(f'Variable {identifier} has not been declared in the current or any enclosing scopes')
        return False

        # return false when types mismatch, otherwise ret true


    def checkTypeMatch(self, vType, eType, var, exp):
        if vType != eType:
            self.error(f'Type Mismatch between {vType} and {eType}')
            return False
        return True
        # return its type or None if not found


    def getMyType(self, identifier):
        for scope in reversed(self.scopes):
            if identifier in scope["variable"]:
                return scope["variable"][identifier]["type"]
        return 'None'


    def declar_var(self, vName, vType):
        self.current_scope()["variable"][vName] = {"type": vType}


    def parse_program(self):
        self.enter_scope("global")
        statements = []
        while self.current_token.type != 'EOF':
            statements.append(self.parse_statement())
            if self.current_token.type == 'DELIMITER':
                self.eat('DELIMITER')
        self.leave_scope()
        return ProgramNode(statements)


    def parse_statement(self):
        if self.current_token.type == 'KEYWORD' and self.current_token.value in ('int', 'float'):
            return self.parse_declaration()
        elif self.current_token.type == 'IDENTIFIER':
            return self.parse_assignment()
        elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'if':
            print(f'Parsing if statement')
            return self.parse_if_statement()
        elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'while':
            print(f'Parsing while loop')
            return self.parse_while_loop()
        else:
            self.error('Invalid statement')
            return None


    def parse_declaration(self):
        type_ = self.current_token.value
        self.eat('KEYWORD')
        identifier = self.current_token.value
        if (self.checkVarNotDeclared(identifier)):
            self.declar_var(identifier, type_)
        print(f'declaration: {self.scopes[0]["variable"]}in global scope')
        self.eat('IDENTIFIER')
        if (self.current_token.value == '='):
            self.eat('OPERATOR')  # Eating the '=' operator
        expr = self.parse_arithmetic_expression()
        if (self.checkTypeMatch(type_, expr.type, identifier, expr)):
            new_node = DeclarationNode(identifier, expr, type_)
            return new_node
        else:
            new_node = DeclarationNode(identifier, expr, 'None')
            return new_node


    def parse_assignment(self):
        identifier = self.current_token.value
        self.eat('IDENTIFIER')
        self.eat('OPERATOR')  # Eating the '=' operator
        expr = self.parse_arithmetic_expression()
        self.checkVarUse(identifier)
        var_type = self.getMyType(identifier)
        if self.checkTypeMatch(var_type, expr.type, identifier, expr):
            node = AssignmentNode(identifier, expr)
            return node


    def parse_arithmetic_expression(self):
        term = self.parse_term()
        while self.current_token.type == 'OPERATOR' and self.current_token.value in ('+', '-'):
            operator = self.current_token.value
            self.eat('OPERATOR')
            right = self.parse_term()
            if (self.checkTypeMatch(term.type, right.type, term, right)):
                node = ArithmeticExpressionNode(operator, term, right, term.type)
                print(f'node type check in + and -: left:{term.type}, right:{right.type}')
                return node
            else:
                node = ArithmeticExpressionNode(operator, term, right, 'None')
                return node
        term_node = ArithmeticExpressionNode('None', term, 'None', term.type)
        return term_node


    def parse_term(self):
        node = self.parse_factor()
        while self.current_token.type == 'OPERATOR' and self.current_token.value in ('*', '/'):
            operator = self.current_token.value
            self.eat('OPERATOR')
            right = self.parse_factor()
            if (self.checkTypeMatch(node.type, right.type, node.value, right.value)):
                term_node = TermNode(operator, node, right, node.type)
                return node
            else:
                term_node = TermNode(operator, node, right, 'None')
                print(f'node type check in * and /: left : {node.type}, right: {right.type}')
                return term_node
        term_node = TermNode('None', node, 'None', node.type)
        return term_node


    def parse_factor(self):
        if self.current_token.type == 'NUMBER':
            value = self.current_token.value
            self.eat('NUMBER')
            node = FactorNode(value, 'int')
            return node
        elif self.current_token.type == 'FNUMBER':
            value = self.current_token.value
            self.eat('FNUMBER')
            node = FactorNode(value, 'float')
            return node
        elif self.current_token.type == 'IDENTIFIER':
            identifier = self.current_token.value
            if (self.checkVarUse(identifier)):
                var_type = self.getMyType(identifier)
            else:
                var_type = 'None'
            self.eat('IDENTIFIER')
            print(f'quick type check!!!!: {self.getMyType(identifier)}')
            node = FactorNode(identifier, var_type)
            return node
        elif self.current_token.type == 'SCOPE' and self.current_token.value == '(':
            self.eat('SCOPE')
            node = self.parse_arithmetic_expression()
            self.eat('SCOPE')
            return node
        else:
            self.error('Invalid factor')


    def parse_if_statement(self):
        self.eat('KEYWORD')  # 'if'
        condition = self.parse_condition()
        self.eat('KEYWORD')  # 'then'
        self.eat('SCOPE')  # '{'
        self.enter_scope("if")
        if_block = []
        while self.current_token.type != 'SCOPE':
            if_block.append(self.parse_statement())
        print(f'if scope:{self.scopes[1]["variable"]}')
        self.eat('SCOPE')  # '}'
        print(f'if scope:{self.scopes[1]["variable"]}')
        self.leave_scope()
        else_block = []
        if self.current_token.type == 'KEYWORD' and self.current_token.value == 'else':
            self.enter_scope("else")
            self.eat('KEYWORD')
            self.eat('SCOPE')  # '{'
            while self.current_token.type != 'SCOPE':
                else_block.append(self.parse_statement())
            self.eat('SCOPE')  # '}'
            self.leave_scope()
        if_node = IfStatementNode(condition, if_block, else_block)
        return if_node


    def parse_while_loop(self):
        self.eat('KEYWORD')  # 'while'
        condition = self.parse_condition()
        self.eat('KEYWORD')  # 'do
        self.eat('SCOPE')  # '{'
        self.enter_scope("while")
        loop_block = []
        while self.current_token.type != 'SCOPE':
            loop_block.append(self.parse_statement())
        print(f'while scope:{self.scopes[1]["variable"]}')
        self.eat('SCOPE')  # '}'
        self.leave_scope()
        while_node = WhileLoopNode(condition, loop_block)
        return while_node


    def parse_condition(self):
        left = self.parse_arithmetic_expression()
        operator = self.current_token.value
        self.eat('OPERATOR')
        right = self.parse_arithmetic_expression()
        cond_node = ConditionNode(left, operator, right)
        return cond_node
@app.route('/', methods=['POST','GET'])
def echo():
    if request.method == 'GET':
        return render_template('index.html')
    print(f"Request headers: {request.headers}")
    if request.content_type != 'application/json':
        return jsonify({"error": "Unsupported Media Type: Content-Type must be 'application/json'"}), 415

    try:
        # 获取 JSON 数据
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        input_text = data.get('text', '')
        return jsonify({"result": input_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'GET':
        return render_template('index.html')

    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({"error": "No valid 'text' provided"}), 400

        text = data['text']
        prefix = 'null'
        postfix = 'null'
        if '+' in text:
            prefix, postfix = text.split('+', 1)
        if prefix.isdigit() and postfix.isdigit():
            outcome = int(prefix) + int(postfix)
            return str(outcome)
        outcome = prefix + postfix
        return jsonify(outcome)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/parse', methods=['POST', 'GET'])
def parse():
    if request.method == 'GET':
        return render_template('index.html')
    try:
        data = request.json
        code = data.get('code', '')
        lexer = Lexer(code)
        parser = Parser(lexer)
        run = parser.parse_program()
        return jsonify(parser.messages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)