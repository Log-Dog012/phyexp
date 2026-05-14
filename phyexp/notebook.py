from IPython.display import Markdown
from pint import Quantity

__all__ = ["table"]

def table(data:dict[str, Quantity], title:str=None, index:bool=True, caption:str=None, label:str=None, **kwargs) -> Markdown:
    """把列式数据生成 Markdown 表格。

    参数：
        data：字典，键为列名，值为列数据序列。
        title：表题。
        index：是否添加索引列。
        caption：表注。
        label：表标签，便于在导出文档中引用。
        kwargs：保留给后续扩展的额外参数。

    返回：
        `IPython.display.Markdown` 对象。
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