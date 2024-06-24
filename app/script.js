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
            }
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