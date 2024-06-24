const express = require('express');
const neo4j = require('neo4j-driver');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

const driver = neo4j.driver(
    process.env.NEO4J_URI, 
    neo4j.auth.basic(process.env.NEO4J_USERNAME, process.env.NEO4J_PASSWORD), 
    { encrypted: 'ENCRYPTION_OFF' }
);
const session = driver.session();

app.use(express.static('app'));

app.get('/env', (req, res) => {
    res.json({
        NEO4J_URI: process.env.NEO4J_URI,
        NEO4J_USERNAME: process.env.NEO4J_USERNAME,
        NEO4J_PASSWORD: process.env.NEO4J_PASSWORD
    });
});

app.get('/nomorPeraturan', async (req, res) => {
    try {
        console.log('Fetching nomor peraturan from Neo4j');
        const result = await session.run('MATCH (p:Peraturan) RETURN p.nomorPeraturan AS nomorPeraturan ORDER BY p.nomorPeraturan');
        const nomorPeraturan = result.records.map(record => record.get('nomorPeraturan'));
        res.json(nomorPeraturan);
    } catch (error) {
        console.error('Error fetching nomor peraturan:', error);
        res.status(500).send('Error fetching nomor peraturan');
    }
});

app.get('/topik', async (req, res) => {
    try {
        console.log('Fetching topik from Neo4j');
        const result = await session.run('MATCH (t:Topik) RETURN t.namaTopik AS namaTopik ORDER BY t.namaTopik');
        const topik = result.records.map(record => record.get('namaTopik'));
        res.json(topik);
    } catch (error) {
        console.error('Error fetching topik:', error);
        res.status(500).send('Error fetching topik');
    }
});

app.get('/bentukPeraturan', async (req, res) => {
    try {
        console.log('Fetching bentuk peraturan from Neo4j');
        const result = await session.run('MATCH (b:Bentuk) RETURN b.namaBentuk AS namaBentuk ORDER BY b.namaBentuk');
        const bentukPeraturan = result.records.map(record => record.get('namaBentuk'));
        res.json(bentukPeraturan);
    } catch (error) {
        console.error('Error fetching bentuk peraturan:', error);
        res.status(500).send('Error fetching bentuk peraturan');
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});