if __name__ == '__main__':
    import json
    import pandas as pd
    import io
    with open('test/refs/ditr_csvs.json') as f:
        obj = json.load(f)
    
    builder = ''
    for k, csv in obj.items():
        df = pd.read_csv(io.StringIO(csv)).fillna('')

        builder += f"## {k}\n"
        builder += df.to_markdown() + '\n\n'

    with open('test/refs/ditr_tables.md', 'w', encoding='utf-8') as f:
        f.write(builder)
        
