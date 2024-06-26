var viz;
var originalLabels = {};

function customObjectToTitleString(node) {
    const properties = node.properties;
    let titleString = "";

    for (let key in properties) {
        if (properties.hasOwnProperty(key)) {
            let formattedKey = key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
            let value = properties[key];

            // Break long strings into multiple lines based on words
            if (typeof value === 'string' && value.length > 30) {
                let words = value.split(' ');
                let lines = [];
                let currentLine = '';

                words.forEach(word => {
                    if ((currentLine + word).length > 30) {
                        lines.push(currentLine.trim());
                        currentLine = word + ' ';
                    } else {
                        currentLine += word + ' ';
                    }
                });

                if (currentLine.length > 0) {
                    lines.push(currentLine.trim());
                }

                value = lines.join('\n'); // Join the lines with newline
            }

            titleString += `${formattedKey}: ${value}\n`;
        }
    }
    return titleString;
}

function init() {
    fetch('/env')
        .then(response => response.json())
        .then(env => {
            draw(env.NEO4J_URI, env.NEO4J_USERNAME, env.NEO4J_PASSWORD);
        });

    // Initialize autocomplete for Nomor Peraturan
    $("#nomorPeraturan").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: "/nomorPeraturan",
                dataType: "json",
                success: function (data) {
                    response(data.filter(item => item.toLowerCase().includes(request.term.toLowerCase())));
                }
            });
        },
        minLength: 2
    });

    // Initialize autocomplete for Nama Topik
    $("#namaTopik").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: "/topik",
                dataType: "json",
                success: function (data) {
                    response(data.filter(item => item.toLowerCase().includes(request.term.toLowerCase())));
                }
            });
        },
        minLength: 2
    });

    // Initialize autocomplete for Bentuk Peraturan
    $("#bentukPeraturan").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: "/bentukPeraturan",
                dataType: "json",
                success: function (data) {
                    response(data.filter(item => item.toLowerCase().includes(request.term.toLowerCase())));
                }
            });
        },
        minLength: 2
    });
    
    // Populate tahun dropdown
    const currentYear = new Date().getFullYear();
    const startYear = 1945;
    let tahunOptions = '<option value="">Pilih Tahun</option>';
    for (let year = currentYear; year >= startYear; year--) {
        tahunOptions += `<option value="${year}">${year}</option>`;
    }
    $("#tahun").html(tahunOptions);
}

function draw(serverUrl, serverUser, serverPassword) {
    var config = {
        containerId: "viz",
        neo4j: {
            serverUrl: serverUrl,
            serverUser: serverUser,
            serverPassword: serverPassword
        },

        visConfig: {
            nodes: {
                shape: "dot",
                size: 16,
                color: {
                    background: "#FFC07A", // Light orange
                    border: "#E76F51", // Darker orange-red
                },
            },
            edges: {
                font: {
                    align: "middle"
                },
                color: {
                    color: "#AABECF", // Light gray-blue
                    highlight: "#6BC0E3"
                },
            },
            layout: {
                improvedLayout: true,
                hierarchical: false
            },
            physics: {
                enabled: true,
                barnesHut: {
                    gravitationalConstant: -8000,
                    centralGravity: 0.3,
                    springLength: 95,
                    springConstant: 0.04,
                    damping: 0.09,
                    avoidOverlap: 1
                },
                stabilization: {
                    iterations: 2000,
                    updateInterval: 25
                }
            },
        },
        
        labels: {
            Peraturan: {
                label: "nomorPeraturan",
                [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                    function: {
                        // show node properties if the node is clicked
                        title: customObjectToTitleString,
                        // Change node color based on label value. If the label value is "Berlaku", the node color will be green, otherwise it will be red.
                        color: (node) => {
                            return node.labels.includes("Berlaku") ? "#5DBB63" : "#FF5733"; // Red for TidakBerlaku, Orange for Berlaku
                        },
                    }
                }
            },
            Topik: {
                label: "namaTopik",
                [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                    function: {
                        label: (node) => {
                            var fullLabel = node.properties.namaTopik;
                            var nodeId = node.identity;
                            originalLabels[nodeId] = fullLabel;
                            if (fullLabel.length >= 10) {
                                return fullLabel.substring(0, 10) + "...";
                            } else {
                                return fullLabel;
                            }
                        }
                    }
                }
            },
            Bentuk: {
                label: "namaBentuk",
                [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                    static: {
                        color: "#8B4513" // Brown color
                    }
                }
            },
            Tahun: {
                label: "tahun",
                [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                    function: {
                        label: (node) => {
                            return node.properties.tahun.toString();
                        }
                    },
                    static: {
                        color: "#4682B4" // Steel blue color
                    }
                }
            }                             
        },

        relationships: {
            [NeoVis.NEOVIS_DEFAULT_CONFIG]: {
                [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
                    function: {
                        label: rel => rel.type
                    }
                }
            }
        },

        initialCypher: "MATCH (n) OPTIONAL MATCH (n)-[r]-(m) RETURN n, r, m LIMIT 100"
    };

    viz = new NeoVis.default(config);
    viz.render();

    // Register click event handler
    viz.registerOnEvent('clickNode', (event) => {
        console.log('Node clicked:', event);
        var nodeId = event.nodeId;
        var fullLabel = originalLabels[nodeId]; // Get original label
        if (fullLabel) {
            console.log('Updating node label:', nodeId, fullLabel);
            viz.network.body.data.nodes.update({ id: nodeId, label: fullLabel });
        } else {
            console.log('Full label not found for node:', nodeId);
        }
    });
}

// Fungsi untuk mengosongkan field input
function clearSearchFields() {
    $("#nomorPeraturan").val('');
    $("#namaTopik").val('');
    $("#tahun").val('');
    $("#bentukPeraturan").val('');
    $("#statusPeraturan").val('');
}

// Fungsi untuk memeriksa hasil query
function checkQueryResults(e) {
    var data = viz.network.body.data;
    var nodesCount = data.nodes.length;
    var edgesCount = data.edges.length;

    if (nodesCount === 0 && edgesCount === 0) {
        alert("Pencarian tidak menemukan hasil.");
        clearSearchFields(); // Kosongkan field input
    }
}

// Fungsi untuk mencari peraturan berdasarkan nomor peraturan
$("#searchPeraturan").click(function () {
    var nomorPeraturan = $("#nomorPeraturan").val();
    if (nomorPeraturan.length > 0) {
        var cypher = `
            MATCH (p1:Peraturan {nomorPeraturan: '${nomorPeraturan}'})-[r1]-(connectedNodes)
            WITH p1, r1, connectedNodes
            OPTIONAL MATCH (p1)-[:MEMILIKI_TOPIK]->(t:Topik)<-[:MEMILIKI_TOPIK]-(p2:Peraturan)
            WITH p1, r1, connectedNodes, t, p2
            OPTIONAL MATCH (p2)-[r2]-(t) // Menambahkan hubungan antara p2 dan topik t
            RETURN p1, r1, connectedNodes, t, p2, r2
        `;
        viz.renderWithCypher(cypher);
        viz.registerOnEvent("completed", checkQueryResults);
    } else {
        alert("Masukkan nomor peraturan.");
    }
});

// Fungsi untuk mencari peraturan berdasarkan kategori
$("#searchKategori").click(function () {
    var namaTopik = $("#namaTopik").val();
    var tahun = $("#tahun").val();
    var bentukPeraturan = $("#bentukPeraturan").val();
    var statusPeraturan = $("#statusPeraturan").val();

    var matchClauses = [];
    var whereClauses = [];
    var withClauses = ['p', 'r1', 'n1'];  // Initialize with mandatory variables

    if (namaTopik) {
        matchClauses.push("(t:Topik {namaTopik: '" + namaTopik + "'})<-[:MEMILIKI_TOPIK]-(p:Peraturan)");
        withClauses.push('t');  // Add 't' if topik search is included
    }
    if (tahun) {
        matchClauses.push("(p)-[:`DITERBITKAN_" + tahun + "`]-(t2:Tahun)");
    }
    if (bentukPeraturan) {
        matchClauses.push("(p)-[:BERBENTUK]->(b:Bentuk {namaBentuk: '" + bentukPeraturan + "'})");
    }
    if (statusPeraturan) {
        whereClauses.push("p:" + statusPeraturan);
    }

    var matchClause = matchClauses.length > 0 ? "MATCH " + matchClauses.join(' MATCH ') : 'MATCH (p:Peraturan)';
    var whereClause = whereClauses.length > 0 ? "WHERE " + whereClauses.join(' AND ') : '';
    var withClause = `WITH ${withClauses.join(', ')}`;

    var cypher = `
        ${matchClause}
        ${whereClause}
        OPTIONAL MATCH (p)-[r1]-(n1)
        ${withClause}
        OPTIONAL MATCH (p)-[:MEMILIKI_TOPIK]->(t:Topik)<-[:MEMILIKI_TOPIK]-(related:Peraturan)
        OPTIONAL MATCH (related)-[r2]-(n2)
        ${tahun ? `WHERE (p)-[:\`DITERBITKAN_${tahun}\`]-(:Tahun) AND (related IS NULL OR (related)-[:\`DITERBITKAN_${tahun}\`]-(:Tahun))` : ''}
        ${bentukPeraturan ? `WHERE (related IS NULL OR (related)-[:BERBENTUK]->(:Bentuk {namaBentuk: '${bentukPeraturan}'}))` : ''}
        RETURN p, ${withClauses.includes('t') ? 't,' : ''} r1, n1, related, r2, n2
    `;
    
    console.log(cypher); // Debug: lihat query yang dibentuk
    viz.renderWithCypher(cypher);
    viz.registerOnEvent("completed", checkQueryResults);
});

$("#reload").click(function () {
    var cypher = $("#cypher").val();

    if (cypher.length > 3) {
        viz.renderWithCypher(cypher);
    } else {
        console.log("reload");
        viz.reload();
    }
});

$("#stabilize").click(function () {
    viz.stabilize();
});