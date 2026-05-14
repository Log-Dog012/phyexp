from IPython.display import Markdown
from pint import Quantity

def table(data:dict[str, Quantity], title:str=None, index:bool=True, caption:str=None, label:str=None, **kwargs) -> Markdown:
    """
    Generate a markdown table from a dictionary of data.

    Parameters:
    - data: A dictionary where keys are column names and values are lists of column values.
    - title: An optional title for the table.
    - index: An optional boolean indicating whether to include an index column.
    - caption: An optional caption for the table.
    - label: An optional label for referencing the table.
    - kwargs: Additional keyword arguments to customize the markdown table generation.

    Returns:
    A string containing the markdown code for the table.
    """
    # Create the header of the table
    headers = list(data.keys())
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"

    # Create the rows of the table
    num_rows = len(next(iter(data.values())))  # Get the number of rows from the first column
    rows = []

    try:
        for i in range(num_rows):
            row = "| " + " | ".join(str(data[header][i]) for header in headers) + " |"
            rows.append(row)
    except IndexError:
        for header in headers:
            if len(data[header]) != num_rows:
                print(f"Column '{header}' has {len(data[header])} rows, but expected {num_rows}.")
        raise ValueError(f"All columns must have the same number of rows.")

    if index:
        # Add an index column if requested
        header_row = "| Index | " + " | ".join(headers) + " |"
        separator_row = "| --- | " + " | ".join(["---"] * len(headers)) + " |"
        rows = [f"| {i} | " + " | ".join(str(data[header][i]) for header in headers) + " |" for i in range(num_rows)]

    # Combine all parts to create the full markdown table
    table_markdown = "\n".join([header_row, separator_row] + rows)

    # Add title, caption, and label if provided
    if title:
        table_markdown = f"表：{title}\n\n" + table_markdown
    if caption:
        table_markdown += f"\n\n*{caption}*"
    if label:
        table_markdown += f"\n\n<!-- {label} -->"

    return Markdown(table_markdown)