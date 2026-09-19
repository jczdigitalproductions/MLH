import os

import pytest
from falkordb import FalkorDB


def get_db():
    host = os.getenv("FALKORDB_HOST")
    if not host:
        pytest.skip("FALKORDB_HOST is not set; configure the database connection first.")

    return FalkorDB(
        host=host,
        port=int(os.getenv("FALKORDB_PORT", "6379")),
        username=os.getenv("FALKORDB_USERNAME"),
        password=os.getenv("FALKORDB_PASSWORD"),
        ssl=os.getenv("FALKORDB_SSL", "true").lower() == "true",
    )


def test_connection_and_basic_query():
    db = get_db()
    graph = db.select_graph("pytest_graph")

    graph.query("MATCH (n) DETACH DELETE n")
    graph.query("CREATE (:Person {name: 'Alice'})-[:KNOWS]->(:Person {name: 'Bob'})")

    result = graph.query("MATCH (p:Person) RETURN p.name ORDER BY p.name").result_set
    names = [row[0] for row in result]

    assert "Alice" in names
    assert "Bob" in names


def test_graph_creation_and_query_are_repeatable():
    db = get_db()
    graph = db.select_graph("pytest_graph")

    graph.query("MATCH (n) DETACH DELETE n")
    graph.query("CREATE (:Person {name: 'Charlie'})")

    result = graph.query("MATCH (p:Person) RETURN COUNT(p) AS total").result_set
    assert result[0][0] == 1