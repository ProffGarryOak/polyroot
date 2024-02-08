from flask import Flask, render_template, request
import numpy as np
import plotly.graph_objs as go

app = Flask(__name__)


def format_equation(coefficients):
    try:
        degree = len(coefficients) - 1

        def term(coef, exp):
            if int(coef) == coef:
                coef = int(coef)
            if exp == 0:
                return str(coef)
            elif exp == 1:
                return f"{coef}x"
            else:
                return f"{coef}x^{exp}"

        def superscript(exp):
            superscript_chars = {"0": "⁰", "1": "¹", "2": "²", "3": "³",
                                 "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
            return "".join(superscript_chars[digit] for digit in str(exp))

        terms = [term(coef, exp) for exp, coef in enumerate(
            reversed(coefficients)) if coef != 0]

        if not terms:
            return "0"
        else:
            formatted_equation = " + ".join(terms[::-1])
            for exp in range(degree, 0, -1):
                formatted_equation = formatted_equation.replace(
                    f"^{exp}", superscript(exp))
            return formatted_equation
    except Exception as e:
        return f"Error: {e}"


def format_imaginary_part(imaginary_part):
    try:
        if imaginary_part == 1:
            return "i"
        elif imaginary_part == -1:
            return "-i"
        elif imaginary_part.is_integer():
            return f"{int(imaginary_part)}i"
        else:
            formatted_imaginary = f"{imaginary_part:.5f}"
            formatted_imaginary = formatted_imaginary.rstrip('0').rstrip(
                '.') if '.' in formatted_imaginary else formatted_imaginary
            return f"{formatted_imaginary}i"
    except Exception as e:
        return f"Error: {e}"


def find_root(coefficients, degree):
    try:
        roots = np.roots(coefficients)
        real_parts = np.real(roots)
        imaginary_parts = np.imag(roots)
        ans = []
        l = len(roots)
        for i in range(l):
            if imaginary_parts[i] == 0:
                if real_parts[i].is_integer():
                    ans.append(str(int(real_parts[i])))
                else:
                    formatted_real = f"{real_parts[i]:.5f}"
                    formatted_real = formatted_real.rstrip('0').rstrip(
                        '.') if '.' in formatted_real else formatted_real
                    ans.append(formatted_real)
            elif real_parts[i] == 0:
                ans.append(format_imaginary_part(imaginary_parts[i]))
            else:
                if real_parts[i].is_integer():
                    real_part_str = str(int(real_parts[i]))
                else:
                    formatted_real = f"{real_parts[i]:.5f}"
                    formatted_real = formatted_real.rstrip('0').rstrip(
                        '.') if '.' in formatted_real else formatted_real
                    real_part_str = formatted_real
                imaginary_part_str = format_imaginary_part(imaginary_parts[i])
                ans.append(f"{real_part_str} + {imaginary_part_str}")
        goodlook = " <br><br> ".join(ans)
        return goodlook
    except Exception as e:
        return f"Error: {e}"


def polynomial_addition(poly1, poly2):
    try:
        result = np.polyadd(poly1, poly2)
        return format_equation(result)
    except Exception as e:
        return f"Error: {e}"


def polynomial_multiplication(poly1, poly2):
    try:
        result = np.polymul(poly1, poly2)
        return format_equation(result)
    except Exception as e:
        return f"Error: {e}"


def polynomial_division(poly1, poly2):
    try:
        quotient, remainder = np.polydiv(poly1, poly2)
        quotient_eq = format_equation(quotient)
        remainder_eq = format_equation(remainder)
        return quotient_eq, remainder_eq
    except Exception as e:
        return f"Error: {e}", None


def polynomial_subtraction(poly1, poly2):
    try:
        result = np.polysub(poly1, poly2)
        return format_equation(result)
    except Exception as e:
        return f"Error: {e}"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/plot_graph', methods=['GET', 'POST'])
def plot_graph():
    if request.method == 'POST':
        try:
            coefficients = list(
                map(float, request.form.get('coefficients').split(',')))
            x_values = np.linspace(-10, 10, 100)
            y_values = np.polyval(coefficients, x_values)
            trace = go.Scatter(x=x_values, y=y_values,
                               mode='lines', name='Polynomial Graph', line=dict(color="#071e3c"))
            layout = go.Layout(
                xaxis=dict(title='X', color='black',
                           showgrid=True, gridcolor='grey'),
                yaxis=dict(title='Y', color='black',
                           showgrid=True, gridcolor='grey'),
                paper_bgcolor='white',
                plot_bgcolor="#daeee9",
                font=dict(color='black'),
                template='plotly_dark',
                margin=dict(l=10, r=50, t=50, b=50)
            )
            fig = go.Figure(data=[trace], layout=layout)
            graph = fig.to_html(
                full_html=False, default_height=500, default_width=600)
            return render_template('plot_graph.html', graph=graph)
        except Exception as e:
            return render_template('plot_graph.html', error="Invalid Input")
    return render_template('plot_graph.html')


@app.route('/find_root', methods=['GET', 'POST'])
def find_root_page():
    roots = None
    poly_eq = None
    if request.method == 'POST':
        try:
            coefficients = list(
                map(float, request.form.get('coefficients').split(',')))
            degree = len(coefficients)-1
            roots = find_root(coefficients, degree)
            poly_eq = format_equation(coefficients)
        except Exception as e:
            return render_template('find_root.html', error="Invalid Input")
    return render_template('find_root.html', roots=roots, poly1=poly_eq)


@app.route('/addition', methods=['GET', 'POST'])
def addition_page():
    result = None
    poly1_eq = None
    poly2_eq = None
    if request.method == 'POST':
        try:
            poly1_eq = format_equation(
                list(map(float, request.form.get('poly1').split(','))))
            poly2_eq = format_equation(
                list(map(float, request.form.get('poly2').split(','))))
            poly1 = list(map(float, request.form.get('poly1').split(',')))
            poly2 = list(map(float, request.form.get('poly2').split(',')))
            result = polynomial_addition(poly1, poly2)
        except Exception as e:
            return render_template('addition.html', error="Invalid Input")
    return render_template('addition.html', result=result, poly1=poly1_eq, poly2=poly2_eq)


@app.route('/multiplication', methods=['GET', 'POST'])
def multiplication_page():
    result = None
    poly1_eq = None
    poly2_eq = None
    if request.method == 'POST':
        try:
            poly1_eq = format_equation(
                list(map(float, request.form.get('poly1').split(','))))
            poly2_eq = format_equation(
                list(map(float, request.form.get('poly2').split(','))))
            poly1 = list(map(float, request.form.get('poly1').split(',')))
            poly2 = list(map(float, request.form.get('poly2').split(',')))
            result = polynomial_multiplication(poly1, poly2)
        except Exception as e:
            return render_template('multiplication.html', error="Invalid Input")
    return render_template('multiplication.html', result=result, poly1=poly1_eq, poly2=poly2_eq)


@app.route('/division', methods=['GET', 'POST'])
def division_page():
    quotient = None
    remainder = None
    poly1_eq = None
    poly2_eq = None
    if request.method == 'POST':
        try:
            poly1_eq = format_equation(
                list(map(float, request.form.get('poly1').split(','))))
            poly2_eq = format_equation(
                list(map(float, request.form.get('poly2').split(','))))
            poly1 = list(map(float, request.form.get('poly1').split(',')))
            poly2 = list(map(float, request.form.get('poly2').split(',')))
            quotient, remainder = polynomial_division(poly1, poly2)
        except Exception as e:
            return render_template('division.html', error="Invalid Input")
    return render_template('division.html', quotient=quotient, remainder=remainder, poly1=poly1_eq, poly2=poly2_eq)


@app.route('/subtraction', methods=['GET', 'POST'])
def subtraction_page():
    result = None
    poly1_eq = None
    poly2_eq = None
    if request.method == 'POST':
        try:
            poly1_eq = format_equation(
                list(map(float, request.form.get('poly1').split(','))))
            poly2_eq = format_equation(
                list(map(float, request.form.get('poly2').split(','))))
            poly1 = list(map(float, request.form.get('poly1').split(',')))
            poly2 = list(map(float, request.form.get('poly2').split(',')))
            result = polynomial_subtraction(poly1, poly2)
        except Exception as e:
            return render_template('subtraction.html', error="Invalid Input")
    return render_template('subtraction.html', result=result, poly1=poly1_eq, poly2=poly2_eq)


if __name__ == '__main__':
    app.run(port=5000)
