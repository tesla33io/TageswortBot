import re

def markdown_escape(text):
    # Characters to escape in Markdown
    escape_chars = r'\\`*_\{\}[]()~`>#\+\-=|.!'
    # Escape backslashes first to prevent escaping the escape character itself
    text = text.replace('\\', r'\\')
    # Escape other markdown special characters using a regular expression
    for char in escape_chars:
        text = re.sub(re.escape(char), rf'\{char}', text)
    return text
