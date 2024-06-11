from neo4j import GraphDatabase


def create_graph(tx, document_info, document_topics):
    nomor_peraturan = document_info["doc_law_number"]
    no = document_info["doc_number"]
    judul = document_info["doc_title"]
    tahun = document_info["doc_year"]
    bentuk = document_info["doc_type"]
    status = document_info["doc_status"]

    if status == "Berlaku":
        status_label = "Berlaku"
    elif status == "Tidak Berlaku":
        status_label = "TidakBerlaku"
    else:
        status_label = "TidakDiketahui"
    
    # create Peraturan node
    tx.run(f"""
        MERGE (p:Peraturan:{status_label} {{nomorPeraturan: $nomor_peraturan}})
        ON CREATE SET p.judul = $judul,
                      p.no = $no,
                      p.tahun = $tahun,
                      p.bentuk = $bentuk
        ON MATCH SET p.judul = $judul,
                     p.no = $no,
                     p.tahun = $tahun,
                     p.bentuk = $bentuk
        """, 
        nomor_peraturan=nomor_peraturan,
        no=no,
        judul=judul,
        tahun=tahun,
        bentuk=bentuk
    )

    # create Bentuk node
    tx.run("""
        MERGE (b:Bentuk {name: $bentuk})
        WITH b
        MATCH (p:Peraturan {nomorPeraturan: $nomor_peraturan})
        MERGE (p)-[:BERBENTUK]->(b)
        SET p.bentuk = null
        RETURN p, b
        """,
        nomor_peraturan=nomor_peraturan,
        bentuk=bentuk
    )
    
    # create Tahun node and specific relationship
    relationship_name = f"DITERBITKAN_{tahun}"
    tx.run(f"""
        MERGE (t:Tahun {{tahun: $tahun}})
        WITH t
        MATCH (p:Peraturan {{nomorPeraturan: $nomor_peraturan}})
        MERGE (p)-[r:{relationship_name}]->(t)
        RETURN p, t, r
        """,
        nomor_peraturan=nomor_peraturan,
        tahun=tahun
    )

    # create Topik nodes and relationships
    for topic in document_topics:
        tx.run(
            """
            MATCH (p:Peraturan {nomorPeraturan: $nomor_peraturan})
            MERGE (t:Topik {namaTopik: $topic})
            MERGE (p)-[:MEMILIKI_TOPIK]->(t)
            RETURN p, t
            """, 
            nomor_peraturan=nomor_peraturan, 
            topic=topic
        )