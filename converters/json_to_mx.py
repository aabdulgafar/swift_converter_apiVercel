def convert_json_to_mx(data: dict) -> str:
    # Dummy pacs.008/pain.001 for demo purpose only
    return f"""<Document>
  <Header>
    <MsgId>{data.get('1', '')}</MsgId>
    <TxRef>{data.get('4', '').split(':20:')[1].splitlines()[0] if ':20:' in data.get('4', '') else 'UNKNOWN'}</TxRef>
  </Header>
</Document>"""
