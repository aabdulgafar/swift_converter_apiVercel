def convert_mt_to_json(mt_message: str) -> dict:
    blocks = {}
    lines = mt_message.strip().split("}")
    for block in lines:
        if block:
            start = block.find("{")
            if start != -1:
                tag = block[start + 1 : block.find(":", start)]
                content = block[block.find(":", start) + 1 :].strip()
                blocks[tag] = content
    return blocks
