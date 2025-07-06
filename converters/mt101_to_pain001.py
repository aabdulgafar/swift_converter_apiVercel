from datetime import datetime

def extract_between(text, start, end):
    if start in text and end in text:
        return text.split(start)[1].split(end)[0]
    return ""

def convert_mt101_to_json(mt_message: str) -> dict:
    fields = {}
    for line in mt_message.splitlines():
        line = line.strip()
        if line.startswith(":") and ":" in line[1:]:
            tag, value = line[1:].split(":", 1)
            fields[tag] = value
        elif line:
            last_key = list(fields.keys())[-1]
            fields[last_key] += " " + line

    uetr = extract_between(mt_message, "{121:", "}")

    def safe_get(key):
        return fields.get(key, "")

    try:
        debtor_bic_block = safe_get("52A").split("\n")
        clearing_member = debtor_bic_block[0].replace("//", "").strip() if debtor_bic_block else ""
        debtor_bic = debtor_bic_block[-1].strip() if len(debtor_bic_block) > 1 else ""

        creditor_address_lines = safe_get("59").split("\n")[1:]
        debtor_name = safe_get("50F").split("1/")[-1].split("3/")[0].strip() if "1/" in safe_get("50F") else ""
        debtor_city_country = safe_get("50F").split("3/")[-1].split("/") if "3/" in safe_get("50F") else ["", ""]
        debtor_city = debtor_city_country[0].strip() if len(debtor_city_country) > 0 else ""
        debtor_country = debtor_city_country[1].strip() if len(debtor_city_country) > 1 else ""

        json_mt = {
            "uetr": uetr,
            "biz_msg_id": safe_get("20") + "-0904-01",
            "msg_id": safe_get("20"),
            "creation_time": datetime.now().isoformat(),
            "execution_date": datetime.strptime(safe_get("30"), "%y%m%d").date().isoformat() if safe_get("30") else "",
            "initiating_party": safe_get("50C"),
            "other_id": safe_get("50F").replace("/OtherID-", ""),
            "debtor_name": debtor_name,
            "debtor_city": debtor_city,
            "debtor_country": debtor_country,
            "debtor_bic": debtor_bic,
            "clearing_member": clearing_member,
            "intermediary_id": safe_get("56C").replace("//CP", ""),
            "creditor_bic": safe_get("57A"),
            "creditor_name": safe_get("59").split("\n")[0].strip(),
            "creditor_address": creditor_address_lines,
            "e2eid": extract_between(safe_get("70"), "///ROC/", "///"),
            "remittance": safe_get("70").split("///URI/")[-1].strip() if "///URI/" in safe_get("70") else "",
            "amount_eur": safe_get("33B").replace("EUR", "").replace(",", "").strip(),
            "amount_gbp": safe_get("32B").replace("GBP", "").replace(",", "").strip(),
            "pmtid": safe_get("21")
        }

        return json_mt
    except Exception as e:
        raise ValueError(f"Error parsing MT101: {str(e)}")

def convert_json_to_pain001(json_mt: dict) -> str:
    now = datetime.now().isoformat()
    apphdr = f"""<AppHdr xmlns="urn:iso:std:iso:20022:tech:xsd:head.001.001.02">
    <Fr><OrgId><Id><OrgId><AnyBIC>{json_mt['initiating_party']}</AnyBIC></OrgId></Id></OrgId></Fr>
    <To><FIId><FinInstnId><BICFI>{json_mt['debtor_bic']}</BICFI></FinInstnId></FIId></To>
    <BizMsgIdr>{json_mt['biz_msg_id']}</BizMsgIdr>
    <MsgDefIdr>pain.001.001.09</MsgDefIdr>
    <BizSvc>swift.scoreplus.01</BizSvc>
    <CreDt>{now}</CreDt>
</AppHdr>"""

    address_xml = "".join(f"<AdrLine>{line.strip()}</AdrLine>" for line in json_mt["creditor_address"])

    document = f"""<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
<CstmrCdtTrfInitn>
    <GrpHdr>
        <MsgId>{json_mt['msg_id']}</MsgId>
        <CreDtTm>{now}</CreDtTm>
        <NbOfTxs>1</NbOfTxs>
        <InitgPty>
            <Id><OrgId><AnyBIC>{json_mt['initiating_party']}</AnyBIC></OrgId></Id>
        </InitgPty>
    </GrpHdr>
    <PmtInf>
        <PmtInfId>{json_mt['pmtid']}</PmtInfId>
        <PmtMtd>TRF</PmtMtd>
        <ReqdExctnDt><Dt>{json_mt['execution_date']}</Dt></ReqdExctnDt>
        <Dbtr>
            <Nm>{json_mt['debtor_name']}</Nm>
            <PstlAdr>
                <TwnNm>{json_mt['debtor_city']}</TwnNm>
                <Ctry>{json_mt['debtor_country']}</Ctry>
            </PstlAdr>
        </Dbtr>
        <DbtrAcct>
            <Id><Othr><Id>{json_mt['other_id']}</Id></Othr></Id>
        </DbtrAcct>
        <DbtrAgt>
            <FinInstnId>
                <BICFI>{json_mt['debtor_bic']}</BICFI>
                <ClrSysMmbId>
                    <ClrSysId><Cd>GBDSC</Cd></ClrSysId>
                    <MmbId>{json_mt['clearing_member']}</MmbId>
                </ClrSysMmbId>
            </FinInstnId>
        </DbtrAgt>
        <CdtTrfTxInf>
            <PmtId>
                <EndToEndId>{json_mt['e2eid']}</EndToEndId>
                <UETR>{json_mt['uetr']}</UETR>
            </PmtId>
            <Amt>
                <EqvtAmt>
                    <Amt Ccy="EUR">{json_mt['amount_eur']}</Amt>
                    <CcyOfTrf>GBP</CcyOfTrf>
                </EqvtAmt>
            </Amt>
            <ChrgBr>DEBT</ChrgBr>
            <IntrmyAgt1>
                <FinInstnId>
                    <ClrSysMmbId>
                        <ClrSysId><Cd>USPID</Cd></ClrSysId>
                        <MmbId>{json_mt['intermediary_id']}</MmbId>
                    </ClrSysMmbId>
                </FinInstnId>
            </IntrmyAgt1>
            <CdtrAgt>
                <FinInstnId>
                    <BICFI>{json_mt['creditor_bic']}</BICFI>
                    <ClrSysMmbId>
                        <ClrSysId><Cd>CHSIC</Cd></ClrSysId>
                        <MmbId>0008</MmbId>
                    </ClrSysMmbId>
                </FinInstnId>
            </CdtrAgt>
            <Cdtr>
                <Nm>{json_mt['creditor_name']}</Nm>
                <PstlAdr>{address_xml}</PstlAdr>
            </Cdtr>
            <Purp><Cd>INTC</Cd></Purp>
            <RgltryRptg><DbtCdtRptgInd>CRED</DbtCdtRptgInd></RgltryRptg>
            <RltdRmtInf><RmtId>Related remittance information 254</RmtId></RltdRmtInf>
            <RmtInf><Ustrd>{json_mt['remittance']}</Ustrd></RmtInf>
        </CdtTrfTxInf>
    </PmtInf>
</CstmrCdtTrfInitn>
</Document>"""

    return apphdr + "\n" + document
