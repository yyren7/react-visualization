import graphviz

try:
    with open('database_schema_v16.md', 'r') as f:
        dot_content = f.read()

    dot = graphviz.Source(dot_content)
    dot.render('database_schema_v16_improved', format='png', view=False)
    print("Improved database schema visualization saved to database_schema_v16_improved.png")

except Exception as e:
    print(f"Error generating improved database schema visualization: {e}")