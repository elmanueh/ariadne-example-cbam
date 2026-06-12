from pathlib import Path

from rdflib import Graph


try:
    udf
except NameError:

    def udf(**_kwargs):
        def decorator(function):
            return function

        return decorator


def _udfs_file_path() -> Path | None:
    file_path = globals().get("__file__")
    if isinstance(file_path, str):
        return Path(file_path).resolve()
    return None


def _workspace_root() -> Path:
    udfs_file_path = _udfs_file_path()
    if udfs_file_path is not None:
        candidate = udfs_file_path.parent.parent
        if (candidate / "ontologies").exists():
            return candidate

    return Path.cwd().resolve()


UDFS_FILE_PATH = _udfs_file_path()
UDFS_DIR = UDFS_FILE_PATH.parent if UDFS_FILE_PATH is not None else Path.cwd().resolve()
WORKSPACE_ROOT = _workspace_root()
COUNTRY_PLUS_PATH = WORKSPACE_ROOT / "ontologies" / "CountryPlus.ttl"
ONTOLOGY_ALIASES = {
    "https://purl.org/cbam/CountryPlus": COUNTRY_PLUS_PATH,
    "https://purl.org/cbam/CountryPlus/": COUNTRY_PLUS_PATH,
    "https://purl.org/cbam/CountryPlus/1.0": COUNTRY_PLUS_PATH,
}
PREFIXES = {
    "ontology-geonames": "https://www.geonames.org/ontology#",
}

ontologies = {}


def _resolve_ontology_path(ontology_path: str) -> str:
    stripped = ontology_path.strip()
    alias = ONTOLOGY_ALIASES.get(stripped)
    if alias is not None:
        return str(alias)

    if "://" in stripped:
        return stripped

    candidate = Path(stripped).expanduser()
    if candidate.is_absolute():
        return str(candidate)

    for base_path in (WORKSPACE_ROOT, Path.cwd(), UDFS_DIR):
        resolved = (base_path / candidate).resolve()
        if resolved.exists():
            return str(resolved)

    return str((WORKSPACE_ROOT / candidate).resolve())


def _expand_iri(value: str) -> str:
    if "://" in value:
        return value

    prefix, separator, local_name = value.partition(":")
    if separator and prefix in PREFIXES:
        return f"{PREFIXES[prefix]}{local_name}"

    return value


def _ontology(ontology_path: str) -> Graph:
    resolved_path = _resolve_ontology_path(ontology_path)
    if resolved_path not in ontologies:
        graph = Graph()
        graph.parse(resolved_path, format="ttl")
        ontologies[resolved_path] = graph

    return ontologies[resolved_path]


@udf(
    fun_id="http://functions.com/get_property_value",
    ontology_path="http://functions.com/parameters#ontologyParam",
    entity_iri="http://functions.com/parameters#entityParam",
    property_iri="http://functions.com/parameters#propertyParam",
)
def get_property_value(ontology_path: str, entity_iri: str, property_iri: str) -> str:
    ontology = _ontology(ontology_path)
    expanded_property_iri = _expand_iri(property_iri)

    results = list(
        ontology.query(f"""
           SELECT ?value
           WHERE {{ <{entity_iri}> <{expanded_property_iri}> ?value }}
    """)
    )

    if len(results) == 0:
        return ""
    return str(results.pop()[0])


@udf(
    fun_id="http://functions.com/belongs_to_class",
    ontology_path="http://functions.com/parameters#ontologyParam",
    instance_iri="http://functions.com/parameters#instanceParam",
    class_iri="http://functions.com/parameters#classParam",
)
def belong_to_class(ontology_path: str, instance_iri: str, class_iri: str) -> bool:
    ontology = _ontology(ontology_path)

    result = ontology.query(f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        ASK
        WHERE {{ <{instance_iri}> rdf:type/rdfs:subClassOf* <{class_iri}> }}
    """)
    return bool(result.askAnswer)


@udf(
    fun_id="http://functions.com/get_belonging_classes",
    ontology_path="http://functions.com/parameters#ontologyParam",
    instance_iri="http://functions.com/parameters#instanceParam",
)
def get_belonging_classes(ontology_path: str, instance_iri: str) -> list:
    ontology = _ontology(ontology_path)

    results = list(
        ontology.query(f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            SELECT ?class
            WHERE {{ <{instance_iri}> rdf:type ?class }}
    """)
    )
    return [str(result[0]) for result in results]


if __name__ == "__main__":
    ontology_path = str(COUNTRY_PLUS_PATH)
    instance_iri = "https://sws.geonames.org/146669"
    class_iri = "https://ontology.siemens-energy.com/cbam/EU_Member_State"
    x = belong_to_class(ontology_path, instance_iri, class_iri)
    print(x)
    instance_iri = "https://sws.geonames.org/102358"
    x = belong_to_class(ontology_path, instance_iri, class_iri)
    print(x)
    x = get_belonging_classes(ontology_path, instance_iri)
    print(x)
