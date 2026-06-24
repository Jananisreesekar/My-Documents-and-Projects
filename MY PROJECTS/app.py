from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# -------------------- ROUTES --------------------

@app.route("/")
def entry():
    return render_template("entry.html")

@app.route("/intro")
def intro():
    return render_template("intro.html")

@app.route("/steps")
def steps():
    return render_template("steps.html")

@app.route("/main")
def main():
    return render_template("index.html")


# -------------------- CUSTOM INDENTATION CHECK --------------------

def check_indentation(code):
    lines = code.split("\n")

    for i, line in enumerate(lines, start=1):
        if line.strip() == "":
            continue

        spaces = len(line) - len(line.lstrip(" "))

        # ❌ Not multiple of 4 spaces
        if spaces % 4 != 0:
            return i

    return None


# -------------------- PYTHON CHECK API --------------------

@app.route('/check_code', methods=['POST'])
def check_code():

    data = request.get_json()
    code = data.get('code', '')

    # 🔥 STEP 1: CUSTOM INDENTATION CHECK
    indent_line = check_indentation(code)

    if indent_line:
        return jsonify({
            "status": "error",
            "error": f"Wrong indentation in line {indent_line}",
            "suggestion": f"Add proper spaces before line {indent_line}"
        })

    try:
        # ✅ Compile
        compiled_code = compile(code, '<string>', 'exec')

        # ✅ Execute
        exec(compiled_code, {})

        return jsonify({
            "status": "success"
        })

    # -------------------- INDENTATION ERRORS --------------------

    except IndentationError as e:
        msg = str(e)
        line = e.lineno

        if "expected an indented block" in msg:

            if code.strip().endswith(":"):
                error = f"Incomplete code near line {line}"
                suggestion = "Add a statement inside the block"

            else:
                error = f"Indentation missing after ':' in line {line}"
                suggestion = f"Add indentation to line {line}"

        elif "unexpected indent" in msg:
            error = f"Unexpected indentation in line {line}"
            suggestion = f"Remove extra spaces in line {line}"

        else:
            error = f"Indentation issue in line {line}"
            suggestion = f"Fix indentation in line {line}"

        return jsonify({
            "status": "error",
            "error": error,
            "suggestion": suggestion
        })

    # -------------------- SYNTAX ERRORS --------------------

    except SyntaxError as e:
        msg = str(e)
        line = e.lineno

        if "expected ':'" in msg:
            error = f"Colon missing in line {line}"
            suggestion = f"Put ':' at the end of line {line}"

        elif "was never closed" in msg:
            error = f"Missing closing bracket in line {line}"
            suggestion = "Add the closing bracket ')'"

        elif (code.count('"') % 2 != 0) or (code.count("'") % 2 != 0):
            error = f"Missing closing quotes in line {line}"
            suggestion = "Close the string properly"

        elif "EOF while parsing" in msg:
            error = f"Incomplete code near line {line}"
            suggestion = "Complete the code properly"

        elif "invalid syntax" in msg:
            error = f"Syntax error in line {line}"
            suggestion = f"Check syntax in line {line}"

        else:
            error = f"Syntax error in line {line}"
            suggestion = "Check your code"

        return jsonify({
            "status": "error",
            "error": error,
            "suggestion": suggestion
        })

    # -------------------- NAME ERROR --------------------

    except NameError as e:
        msg = str(e)
        var_name = msg.split("'")[1]

        return jsonify({
            "status": "error",
            "error": f"Variable '{var_name}' is not defined",
            "suggestion": f"Define the variable '{var_name}' before using it"
        })

    # -------------------- OTHER ERRORS --------------------

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": "Execution error",
            "suggestion": "Check your code logic or variables"
        })


# -------------------- RUN APP --------------------

if __name__ == "__main__":
    app.run(debug=True)