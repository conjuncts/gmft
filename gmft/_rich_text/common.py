from gmft.formatters.common import FormattedTable


class RichComponent:
    def rich_text(self) -> str:
        pass

class Paragraph(RichComponent):
    def __init__(self, content: str) -> None:
        self.content = content
    
    def rich_text(self) -> str:
        return self.content

class TableComponent(RichComponent):
    def __init__(self, table: FormattedTable) -> None:
        self.table = table
        self._text_value = table.df().to_markdown() # + '\n'
    
    def rich_text(self) -> str:
        return self._text_value


    
    
