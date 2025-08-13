# for http requesting qwen, already started via vllm in cli

import openai
import json
import csv
import os
import sys
import time



client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)




json_format= {
    "type": "object",
    "properties": {
        "reasoning": {
            "type": "string",
            "description": "Your full thought process."
        },
        "answer": {
            "type":"integer",
            "enum": [0,1],
            "description": "1 if an exception is expected to occur in this prefix. 0 if an exception is NOT expected to occur in this prefix."
        }
    },
    "required": ["reasoning", "answer"]
}




system_prompt = """
You are an expert Java software developer specializing in unit testing. 
Given a method, docstring, and test prefix, your task is to determine if the developer who wrote the method under test intended for an exception to occur under the conditions of the prefix.


You will output your answer in a Json scheme with two fields: one for your reasoning, and one for your answer.

First, think through the task step by step. Then, output your full thought process into the reasoning field. Ensure you output your full thought process, but keep it short and concise--remember that each output token comes with a cost.

Then, output your answer as either a 1 or 0 in the answer field:
    If an exception is expected to occur when the prefix is executed, output a 1. 
    If an exception is NOT expected to occur when the prefix is executed, output a 0. 
    No other answers are accepted for the "answer" field.


Here are two brief examples of the task. 

Example #1:

    Information:
        Test prefix:                                                                                                                    public void test49()  throws Throwable  {       ClosureCodingConvention closureCodingConvention0 = new ClosureCodingConvention();       SimpleErrorReporter simpleErrorReporter0 = new SimpleErrorReporter();       JSTypeRegistry jSTypeRegistry0 = new JSTypeRegistry(simpleErrorReporter0);       ObjectType objectType0 = jSTypeRegistry0.createAnonymousObjectType();       SemanticReverseAbstractInterpreter semanticReverseAbstractInterpreter0 = new SemanticReverseAbstractInterpreter(closureCodingConvention0, jSTypeRegistry0);       semanticReverseAbstractInterpreter0.getRestrictedByTypeOfResult(objectType0, ""function"", false);   }

  Method under test:                                                                                                              JSType getRestrictedByTypeOfResult(JSType type, String value,                                      boolean resultEqualsValue) {     if (type == null) {       if (resultEqualsValue) {         JSType result = getNativeTypeForTypeOf(value);         return result == null ? getNativeType(CHECKED_UNKNOWN_TYPE) : result;       } else {         return null;       }     }     return type.visit(         new RestrictByOneTypeOfResultVisitor(value, resultEqualsValue));   }

        Docstring:                                                                                                                      /**    * Returns a version of {@code type} that is restricted by some knowledge    * about the result of the {@code typeof} operation.    * <p>    * The behavior of the {@code typeof} operator can be summarized by the    * following table:    * <table>    * <tr><th>type</th><th>result</th></tr>    * <tr><td>{@code undefined}</td><td>""undefined""</td></tr>    * <tr><td>{@code null}</td><td>""object""</td></tr>    * <tr><td>{@code boolean}</td><td>""boolean""</td></tr>    * <tr><td>{@code number}</td><td>""number""</td></tr>    * <tr><td>{@code string}</td><td>""string""</td></tr>    * <tr><td>{@code Object} (which doesn't implement [[Call]])</td>    *     <td>""object""</td></tr>    * <tr><td>{@code Object} (which implements [[Call]])</td>    *     <td>""function""</td></tr>    * </table>    * @param type the type to restrict    * @param value A value known to be equal or not equal to the result of the    *        {@code typeof} operation    * @param resultEqualsValue {@code true} if the {@code typeOf} result is known    *        to equal {@code value}; {@code false} if it is known <em>not</em> to    *        equal {@code value}    * @return the restricted type or null if no version of the type matches the    *         restriction    */

    Reasoning based on this information:
        "The method getRestrictedByTypeOfResult is designed to return a restricted JSType based on the result of a typeof operation. The test case passes an ObjectType, the string ""function"", and false for resultEqualsValue. According to the docstring, when resultEqualsValue is false, the method should return null if no version of the type matches the restriction. Since the ObjectType does not implement [[Call]], its typeof result is ""object"", which does not equal ""function"". Therefore, the method should return null, and no exception is expected."

    Final answer: 0



Example #2:
                                                                                                                                Information:                                                                                                                                                                                                                                                Test prefix:                                                                                                                    public void test03()  throws Throwable  {       Frequency frequency0 = new Frequency();       Object object0 = new Object();                        frequency0.addValue(object0);         ;       }    }

        Method under test:
            public void addValue(Object v) {             addValue((Comparable<?>) v);                 },                                                                                                                                                        Docstring for method under test:                                                                                                /**      * Adds 1 to the frequency count for v.      * <p>      * If other objects have already been added to this Frequency, v must      * be comparable to those that have already been added.      * </p>      *       * @param v the value to add.      * @throws IllegalArgumentException if <code>v</code> is not Comparable,       *         or is not comparable with previous entries      * @deprecated use {@link #addValue(Comparable)} instead      */                                                                                                                                                                 Reasoning based on this information:                                                                                            "The method addValue(Object v) calls addValue((Comparable<?>) v), which expects v to be a Comparable. The test passes an Object, which is not Comparable, leading to a ClassCastException. The docstring warns of IllegalArgumentException, but the actual exception is a ClassCastException, indicating an unexpected exception."

    Final answer: 1
"""


def prompt_model(client, prompt):

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        temperature=0,
        extra_body={
            "guided_json":json_format
        }
    )
    return response.choices[0].message.content.strip()





#main


if len(sys.argv) < 3:
    print("pass in input and output files as command line arguements")

input_csv = sys.argv[1]

output_csv = sys.argv[2]

with open(input_csv, newline='', encoding='utf-8') as infile, \
        open(output_csv, newline='', mode='w', encoding='utf-8') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            header = next(reader)
            writer.writerow(header + ["chatgpt_response"] + ["reasoning"])
            
            idx = 0

            for idx, row in enumerate(reader):

                test_prefix, fm, docstring = row[1:4]

                context = """
                
                /**
     * Get the -1 times the sum of all coefficients in the given array.
     * @param coefficients coefficients to sum
     * @return the -1 times the sum of all coefficients in the given array.
     */
    protected static double getInvertedCoeffiecientSum(final RealVector coefficients) {
        double sum = 0;
        for (double coefficient : coefficients.getData()) {
            sum -= coefficient;
        }
        return sum;
    }

     /**
     * Create the tableau by itself.
     * @param maximize if true, goal is to maximize the objective function
     * @return created tableau
     */
    protected double[][] createTableau(final boolean maximize) {

        // create a matrix of the correct size
        List<LinearConstraint> constraints = getNormalizedConstraints();
        int width = numDecisionVariables + numSlackVariables +
        numArtificialVariables + getNumObjectiveFunctions() + 1; // + 1 is for RHS
        int height = constraints.size() + getNumObjectiveFunctions();
        double[][] matrix = new double[height][width];

        // initialize the objective function rows
        if (getNumObjectiveFunctions() == 2) {
            matrix[0][0] = -1;
        }
        int zIndex = (getNumObjectiveFunctions() == 1) ? 0 : 1;
        matrix[zIndex][zIndex] = maximize ? 1 : -1;
        RealVector objectiveCoefficients =
            maximize ? f.getCoefficients().mapMultiply(-1) : f.getCoefficients();
            copyArray(objectiveCoefficients.getData(), matrix[zIndex], getNumObjectiveFunctions());
            matrix[zIndex][width - 1] =
                maximize ? f.getConstantTerm() : -1 * f.getConstantTerm();

                if (!restrictToNonNegative) {
                    matrix[zIndex][getSlackVariableOffset() - 1] =
                        getInvertedCoeffiecientSum(objectiveCoefficients);
                }

                // initialize the constraint rows
                int slackVar = 0;
                int artificialVar = 0;
                for (int i = 0; i < constraints.size(); i++) {
                    LinearConstraint constraint = constraints.get(i);
                    int row = getNumObjectiveFunctions() + i;

                    // decision variable coefficients
                    copyArray(constraint.getCoefficients().getData(), matrix[row], 1);

                    // x-
                    if (!restrictToNonNegative) {
                        matrix[row][getSlackVariableOffset() - 1] =
                            getInvertedCoeffiecientSum(constraint.getCoefficients());
                    }

                    // RHS
                    matrix[row][width - 1] = constraint.getValue();

                    // slack variables
                    if (constraint.getRelationship() == Relationship.LEQ) {
                        matrix[row][getSlackVariableOffset() + slackVar++] = 1;  // slack
                    } else if (constraint.getRelationship() == Relationship.GEQ) {
                        matrix[row][getSlackVariableOffset() + slackVar++] = -1; // excess
                    }

                    // artificial variables
                    if ((constraint.getRelationship() == Relationship.EQ) ||
                        (constraint.getRelationship() == Relationship.GEQ)) {
                        matrix[0][getArtificialVariableOffset() + artificialVar] = 1;
                        matrix[row][getArtificialVariableOffset() + artificialVar++] = 1;
                    }
                }

                return matrix;
    }



 /**
     * Build a tableau for a linear problem.
     * @param f linear objective function
     * @param constraints linear constraints
     * @param goalType type of optimization goal: either {@link GoalType#MAXIMIZE}
     * or {@link GoalType#MINIMIZE}
     * @param restrictToNonNegative whether to restrict the variables to non-negative values
     * @param epsilon amount of error to accept in floating point comparisons
     */
    SimplexTableau(final LinearObjectiveFunction f,
                   final Collection<LinearConstraint> constraints,
                   final GoalType goalType, final boolean restrictToNonNegative,
                   final double epsilon) {
        this.f                      = f;
        this.constraints            = constraints;
        this.restrictToNonNegative  = restrictToNonNegative;
        this.epsilon                = epsilon;
        this.numDecisionVariables   = getNumVariables() + (restrictToNonNegative ? 0 : 1);
        this.numSlackVariables      = getConstraintTypeCounts(Relationship.LEQ) +
                                      getConstraintTypeCounts(Relationship.GEQ);
        this.numArtificialVariables = getConstraintTypeCounts(Relationship.EQ) +
                                      getConstraintTypeCounts(Relationship.GEQ);
        this.tableau = new RealMatrixImpl(createTableau(goalType == GoalType.MAXIMIZE));
        initialize();
    }



                """
                
                #closure82
                """
                /**
   * Whether this type is meaningfully different from {@code that} type.
   * This is a trickier check than pure equality, because it has to properly
   * handle unknown types.
   *
   * @see <a href="http://www.youtube.com/watch?v=_RpSv3HjpEw">Unknown
   *     unknowns</a>
   */
  public boolean differsFrom(JSType that) {
    // if there are no unknowns, just use normal equality.
    if (!this.isUnknownType() && !that.isUnknownType()) {
      return !this.isEquivalentTo(that);
    }
    // otherwise, they're different iff one is unknown and the other is not.
    return this.isUnknownType() ^ that.isUnknownType();
  }



   /**
   * Checks if two types are equivalent.
   */
  public boolean isEquivalentTo(JSType jsType) {
    if (jsType instanceof ProxyObjectType) {
      return jsType.isEquivalentTo(this);
    }
    // Relies on the fact that for the base {@link JSType}, only one
    // instance of each sub-type will ever be created in a given registry, so
    // there is no need to verify members. If the object pointers are not
    // identical, then the type member must be different.
    return this == jsType;
  }





                """

                #compress14
                """
                @Override
  public void process(Node externs, Node root) {
    NodeTraversal.traverse(compiler, root, this);

    // Code with hidden side-effect code is common, for example
    // accessing "el.offsetWidth" forces a reflow in browsers, to allow this
    // will still allowing local dead code removal in general,
    // protect the "side-effect free" code in the source.
    //
    if (protectSideEffectFreeCode) {
      protectSideEffects();
    }
  }

  /**
   * Traverses a node recursively.
   */
  public static void traverse(
      AbstractCompiler compiler, Node root, Callback cb) {
    NodeTraversal t = new NodeTraversal(compiler, cb);
    t.traverse(root);
  }


  /**
   * Traverses a parse tree recursively.
   */
  public void traverse(Node root) {
    try {
      inputId = NodeUtil.getInputId(root);
      sourceName = "";
      curNode = root;
      pushScope(root);
      traverseBranch(root, null);
      popScope();
    } catch (Exception unexpectedException) {
      throwUnexpectedException(unexpectedException);
    }
  }


   /**
   * Traverses a branch.
   */
  @SuppressWarnings("fallthrough")
  private void traverseBranch(Node n, Node parent) {
    int type = n.getType();
    if (type == Token.SCRIPT) {
      inputId = n.getInputId();
      sourceName = getSourceName(n);
    }

    curNode = n;
    if (!callback.shouldTraverse(this, n, parent)) return;

    switch (type) {
      case Token.FUNCTION:
        traverseFunction(n, parent);
        break;

      default:
        for (Node child = n.getFirstChild(); child != null; ) {
          // child could be replaced, in which case our child node
          // would no longer point to the true next
          Node next = child.getNext();
          traverseBranch(child, n);
          child = next;
        }
        break;
    }

    curNode = n;
    callback.visit(this, n, parent);
  }


  @Override public void visit(NodeTraversal t, Node n, Node parent) {
      if (NodeUtil.isExprAssign(n)) {
        Node assign = n.getFirstChild();
        Node lhs = assign.getFirstChild();
        if (lhs.isGetProp() && isMarkedExpose(assign)) {
          exposedProperties.add(lhs.getLastChild().getString());
        }
      } else if (n.isStringKey() && isMarkedExpose(n)) {
        exposedProperties.add(n.getString());
      }
    }




                """


                #jsoup50
                """
        // reads bytes first into a buffer, then decodes with the appropriate charset. done this way to support
    // switching the chartset midstream when a meta http-equiv tag defines the charset.
    // todo - this is getting gnarly. needs a rewrite.
    static Document parseByteData(ByteBuffer byteData, String charsetName, String baseUri, Parser parser) {
        String docData;
        Document doc = null;

        // look for BOM - overrides any other header or input

        if (charsetName == null) { // determine from meta. safe parse as UTF-8
            // look for <meta http-equiv="Content-Type" content="text/html;charset=gb2312"> or HTML5 <meta charset="gb2312">
            docData = Charset.forName(defaultCharset).decode(byteData).toString();
            doc = parser.parseInput(docData, baseUri);
            Element meta = doc.select("meta[http-equiv=content-type], meta[charset]").first();
            if (meta != null) { // if not found, will keep utf-8 as best attempt
                String foundCharset = null;
                if (meta.hasAttr("http-equiv")) {
                    foundCharset = getCharsetFromContentType(meta.attr("content"));
                }
                if (foundCharset == null && meta.hasAttr("charset")) {
                    try {
                        if (Charset.isSupported(meta.attr("charset"))) {
                            foundCharset = meta.attr("charset");
                        }
                    } catch (IllegalCharsetNameException e) {
                        foundCharset = null;
                    }
                }

                if (foundCharset != null && foundCharset.length() != 0 && !foundCharset.equals(defaultCharset)) { // need to re-decode
                    foundCharset = foundCharset.trim().replaceAll("[\"']", "");
                    charsetName = foundCharset;
                    byteData.rewind();
                    docData = Charset.forName(foundCharset).decode(byteData).toString();
                    doc = null;
                }
            }
        } else { // specified by content type header (or by user on file load)
            Validate.notEmpty(charsetName, "Must set charset arg to character set of file to parse. Set to null to attempt to detect from HTML");
            docData = Charset.forName(charsetName).decode(byteData).toString();
        }
        if (docData.length() > 0 && docData.charAt(0) == UNICODE_BOM) {
            byteData.rewind();
            docData = Charset.forName(defaultCharset).decode(byteData).toString();
            docData = docData.substring(1);
            charsetName = defaultCharset;
            doc = null;
        }
        if (doc == null) {
            doc = parser.parseInput(docData, baseUri);
            doc.outputSettings().charset(charsetName);
        }
        return doc;
    }


public Document parseInput(String html, String baseUri) {
        errors = isTrackErrors() ? ParseErrorList.tracking(maxErrors) : ParseErrorList.noTracking();
        return treeBuilder.parse(html, baseUri, errors);
    }



    /**
     * Find elements that match the {@link Selector} CSS query, with this element as the starting context. Matched elements
     * may include this element, or any of its children.
     * <p>
     * This method is generally more powerful to use than the DOM-type {@code getElementBy*} methods, because
     * multiple filters can be combined, e.g.:
     * </p>
     * <ul>
     * <li>{@code el.select("a[href]")} - finds links ({@code a} tags with {@code href} attributes)
     * <li>{@code el.select("a[href*=example.com]")} - finds links pointing to example.com (loosely)
     * </ul>
     * <p>
     * See the query syntax documentation in {@link org.jsoup.select.Selector}.
     * </p>
     *
     * @param cssQuery a {@link Selector} CSS-like query
     * @return elements that match the query (empty if none match)
     * @see org.jsoup.select.Selector
     * @throws Selector.SelectorParseException (unchecked) on an invalid CSS query.
     */
    public Elements select(String cssQuery) {
        return Selector.select(cssQuery, this);
    }




                """

                #jsoup50
                """
                private IRFactory(String sourceString,
                    String sourceName,
                    Config config,
                    ErrorReporter errorReporter) {
    this.sourceString = sourceString;
    this.sourceName = sourceName;
    this.config = config;
    this.errorReporter = errorReporter;
    this.transformDispatcher = new TransformDispatcher();
    // The template node properties are applied to all nodes in this transform.
    this.templateNode = createTemplateNode();
  }


  private Node transform(AstNode node) {
    JSDocInfo jsDocInfo = handleJsDoc(node);
    Node irNode = justTransform(node);
    if (jsDocInfo != null) {
      irNode.setJSDocInfo(jsDocInfo);
    }

    // If we have a named function, set the position to that of the name.
    if (irNode.getType() == Token.FUNCTION &&
        irNode.getFirstChild().getLineno() != -1) {
      irNode.setLineno(irNode.getFirstChild().getLineno());
      irNode.setCharno(irNode.getFirstChild().getCharno());
    } else {
      if (irNode.getLineno() == -1) {
        // If we didn't already set the line, then set it now.  This avoids
        // cases like ParenthesizedExpression where we just return a previous
        // node, but don't want the new node to get its parent's line number.
        int lineno = node.getLineno();
        irNode.setLineno(lineno);
        int charno = position2charno(node.getAbsolutePosition());
        irNode.setCharno(charno);
      }
    }
    return irNode;
  }

     private JSDocInfo handleJsDoc(AstNode node) {
    Comment comment = node.getJsDocNode();
    if (comment != null) {
      JsDocInfoParser jsDocParser = createJsDocInfoParser(comment);
      comment.setParsed(true);
      if (!handlePossibleFileOverviewJsDoc(jsDocParser)) {
        return jsDocParser.retrieveAndResetParsedJSDocInfo();
      }
    }
    return null;
  }



   private Node justTransform(AstNode node) {
    return transformDispatcher.process(node);
  }


    public T process(AstNode node) {
    switch (node.getType()) {
      case Token.ADD:
      case Token.AND:
      case Token.BITAND:
      case Token.BITOR:
      case Token.BITXOR:
      case Token.COMMA:
      case Token.DIV:
      case Token.EQ:
      case Token.GE:
      case Token.GT:
      case Token.IN:
      case Token.INSTANCEOF:
      case Token.LE:
      case Token.LSH:
      case Token.LT:
      case Token.MOD:
      case Token.MUL:
      case Token.NE:
      case Token.OR:
      case Token.RSH:
      case Token.SHEQ:
      case Token.SHNE:
      case Token.SUB:
      case Token.URSH:
        return processInfixExpression((InfixExpression) node);
      case Token.ARRAYLIT:
        return processArrayLiteral((ArrayLiteral) node);
      case Token.ASSIGN:
      case Token.ASSIGN_ADD:
      case Token.ASSIGN_BITAND:
      case Token.ASSIGN_BITOR:
      case Token.ASSIGN_BITXOR:
      case Token.ASSIGN_DIV:
      case Token.ASSIGN_LSH:
      case Token.ASSIGN_MOD:
      case Token.ASSIGN_MUL:
      case Token.ASSIGN_RSH:
      case Token.ASSIGN_SUB:
      case Token.ASSIGN_URSH:
        return processAssignment((Assignment) node);
      case Token.BITNOT:
      case Token.DEC:
      case Token.DELPROP:
      case Token.INC:
      case Token.NEG:
      case Token.NOT:
      case Token.POS:
      case Token.TYPEOF:
      case Token.VOID:
        return processUnaryExpression((UnaryExpression) node);
      case Token.BLOCK:
        if (node instanceof Block) {
          return processBlock((Block) node);
        } else  if (node instanceof Scope) {
          return processScope((Scope) node);
        } else {
          throw new IllegalStateException("Unexpected node type.  class: " +
                                          node.getClass() +
                                          " type: " +
                                          Token.typeToName(node.getType()));
        }
      case Token.BREAK:
        return processBreakStatement((BreakStatement) node);
      case Token.CALL:
        return processFunctionCall((FunctionCall) node);
      case Token.CASE:
      case Token.DEFAULT:
        return processSwitchCase((SwitchCase) node);
      case Token.CATCH:
      case Token.FINALLY:
        return processCatchClause((CatchClause) node);
      case Token.COLON:
        return processObjectProperty((ObjectProperty) node);
      case Token.CONTINUE:
        return processContinueStatement((ContinueStatement) node);
      case Token.DO:
        return processDoLoop((DoLoop) node);
      case Token.EMPTY:
        return processEmptyExpression((EmptyExpression) node);
      case Token.EXPR_RESULT:
      case Token.EXPR_VOID:
        if (node instanceof ExpressionStatement) {
          return processExpressionStatement((ExpressionStatement) node);
        } else  if (node instanceof LabeledStatement) {
          return processLabeledStatement((LabeledStatement) node);
        } else {
          throw new IllegalStateException("Unexpected node type.  class: " +
                                          node.getClass() +
                                          " type: " +
                                          Token.typeToName(node.getType()));
        }
      case Token.DEBUGGER:
      case Token.FALSE:
      case Token.NULL:
      case Token.THIS:
      case Token.TRUE:
        return processKeywordLiteral((KeywordLiteral) node);
      case Token.FOR:
        if (node instanceof ForInLoop) {
          return processForInLoop((ForInLoop) node);
        } else  if (node instanceof ForLoop) {
          return processForLoop((ForLoop) node);
        } else {
          throw new IllegalStateException("Unexpected node type.  class: " +
                                          node.getClass() +
                                          " type: " +
                                          Token.typeToName(node.getType()));
        }
      case Token.FUNCTION:
        return processFunctionNode((FunctionNode) node);
      case Token.GETELEM:
        return processElementGet((ElementGet) node);
      case Token.GETPROP:
        return processPropertyGet((PropertyGet) node);
      case Token.HOOK:
        return processConditionalExpression((ConditionalExpression) node);
      case Token.IF:
        return processIfStatement((IfStatement) node);
      case Token.LABEL:
        return processLabel((Label) node);
      case Token.LP:
        return processParenthesizedExpression((ParenthesizedExpression) node);
      case Token.NAME:
        return processName((Name) node);
      case Token.NEW:
        return processNewExpression((NewExpression) node);
      case Token.NUMBER:
        return processNumberLiteral((NumberLiteral) node);
      case Token.OBJECTLIT:
        return processObjectLiteral((ObjectLiteral) node);
      case Token.REGEXP:
        return processRegExpLiteral((RegExpLiteral) node);
      case Token.RETURN:
        return processReturnStatement((ReturnStatement) node);
      case Token.SCRIPT:
        return processAstRoot((AstRoot) node);
      case Token.STRING:
        return processStringLiteral((StringLiteral) node);
      case Token.SWITCH:
        return processSwitchStatement((SwitchStatement) node);
      case Token.THROW:
        return processThrowStatement((ThrowStatement) node);
      case Token.TRY:
        return processTryStatement((TryStatement) node);
      case Token.CONST:
      case Token.VAR:
        if (node instanceof VariableDeclaration) {
          return processVariableDeclaration((VariableDeclaration) node);
        } else  if (node instanceof VariableInitializer) {
          return processVariableInitializer((VariableInitializer) node);
        } else {
          throw new IllegalStateException("Unexpected node type.  class: " +
                                          node.getClass() +
                                          " type: " +
                                          Token.typeToName(node.getType()));
        }
      case Token.WHILE:
        return processWhileLoop((WhileLoop) node);
      case Token.WITH:
        return processWithStatement((WithStatement) node);
    }
    return processIllegalToken(node);
  }



  @Override
    Node processFunctionNode(FunctionNode functionNode) {
      Name name = functionNode.getFunctionName();
      Boolean isUnnamedFunction = false;
      if (name == null) {
        name = new Name();
        name.setIdentifier("");
        isUnnamedFunction = true;
      }
      Node node = newNode(Token.FUNCTION);
      Node newName = transform(name);
      if (isUnnamedFunction) {
        // Old Rhino tagged the empty name node with the line number of the
        // declaration.
        newName.setLineno(functionNode.getLineno());
        // TODO(bowdidge) Mark line number of paren correctly.
        // Same problem as below - the left paren might not be on the
        // same line as the function keyword.
        int lpColumn = functionNode.getAbsolutePosition() +
            functionNode.getLp();
        newName.setCharno(position2charno(lpColumn));
      }
                


                """




                #csv5
                """
                    /**
     * Prints all the objects in the given collection.
     *
     * @param values
     *            the values to print.
     * @throws IOException
     *             If an I/O error occurs
     */
    public void printRecords(final Iterable<?> values) throws IOException {
        for (final Object value : values) {
            if (value instanceof Object[]) {
                this.printRecord((Object[]) value);
            } else if (value instanceof Iterable) {
                this.printRecord((Iterable<?>) value);
            } else {
                this.printRecord(value);
            }
        }
    }


     /**
     * Prints a single line of delimiter separated values. The values will be quoted if needed. Quotes and newLine
     * characters will be escaped.
     *
     * @param values
     *            values to output.
     * @throws IOException
     *             If an I/O error occurs
     */
    public void printRecord(final Object... values) throws IOException {
        for (final Object value : values) {
            print(value);
        }
        println();
    }



                """

    #compress 44
                """
                /** * Reads a single byte from the stream  * @throws IOException if the underlying stream throws or the
     * stream is exhausted and the Checksum doesn't match the expected
     * value
     */  @Override  public int read() throws IOException { final int ret = in.read(); if (ret >= 0) {
            checksum.update(ret);
        }
        return ret;
    }  /**
     * Updates the current checksum with the specified array of bytes.
     *
     * @param b the byte array to update the checksum with
     * @param off the start offset of the data
     * @param len the number of bytes to use for the update
     */
    public void update(byte[] b, int off, int len);

         /**
     * Updates the current checksum with the bytes from the specified buffer.
     *
     * The checksum is updated with the remaining bytes in the buffer, starting
     * at the buffer's position. Upon return, the buffer's position will be
     * updated to its limit; its limit will not have been changed.
     *
     * @apiNote For best performance with DirectByteBuffer and other ByteBuffer
     * implementations without a backing array implementers of this interface
     * should override this method.
     *
     * @implSpec The default implementation has the following behavior.<br>
     * For ByteBuffers backed by an accessible byte array.
     * <pre>{@code
     * update(buffer.array(),
     *        buffer.position() + buffer.arrayOffset(),
     *        buffer.remaining());
     * }</pre>
     * For ByteBuffers not backed by an accessible byte array.
     * <pre>{@code
     * byte[] b = new byte[Math.min(buffer.remaining(), 4096)];
     * while (buffer.hasRemaining()) {
     *     int length = Math.min(buffer.remaining(), b.length);
     *     buffer.get(b, 0, length);
     *     update(b, 0, length);
     * }
     * }</pre>
     *
     * @param buffer the ByteBuffer to update the checksum with
     *
     * @throws NullPointerException
     *         if {@code buffer} is {@code null}
     *
     * @since 9
     */
    default public void update(ByteBuffer buffer) {
        int pos = buffer.position();
        int limit = buffer.limit();
        assert (pos <= limit);
        int rem = limit - pos;
        if (rem <= 0) {
            return;
        }
        if (buffer.hasArray()) {
            update(buffer.array(), pos + buffer.arrayOffset(), rem);
        } else {
            byte[] b = new byte[Math.min(buffer.remaining(), 4096)];
            while (buffer.hasRemaining()) {
                int length = Math.min(buffer.remaining(), b.length);
                buffer.get(b, 0, length);
                update(b, 0, length);
            }
        }
                buffer.position(limit);
                }

                """

                prompt = f"Based on the following information, is an exception expected to occur when the unit test is executed? \n\nHere is the information: \n\n Method under test: {fm} Additional source methods: {context} \n\n Docstring: {docstring} \n\n Test prefix: {test_prefix}"

                response = prompt_model(client, prompt)

                try: 
                    parsed_response = json.loads(response)
                    reasoning_only = parsed_response["reasoning"]
                    answer_only = parsed_response["answer"]
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    print(f"Raw response: {repr(response)}")
                    answer_only = "JSON_ERROR"
                    reasoning_only = "JSON_ERROR"
                    #input("Press Enter to continue...")
                except KeyError as e:
                    print(f"Missing field in JSON: {e}")
                    print(f"Parsed response: {parsed_response}")
                    answer_only = "MISSING_FIELD"
                    #input("Press Enter to continue...")
                
                time.sleep(1)
                print()
                print()
                print(idx)
                print()
                writer.writerow(row + [answer_only] + [reasoning_only])
                idx += 1
                

