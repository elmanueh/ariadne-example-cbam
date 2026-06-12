# ariadne-example-cbam

Minimal CBAM case study for **Ariadne**.

This example shows how Ariadne turns small CBAM installation data into RDF.

## Contents

| Path              | Description                           |
| ----------------- | ------------------------------------- |
| `datasources/`    | Input CSV files.                      |
| `functions/`      | UDFs used by the mapping.             |
| `knowledgegraph/` | Generated RDF graph.                  |
| `mappings/`       | YARRRML mapping.                      |
| `ontologies/`     | CBAM, CountryPlus and GeoNames terms. |
| `ariadne.yml`     | Ariadne pipeline configuration.       |

## Case Study

The source data describes a cement production installation: name, economic
activity, address, country, coordinates, representative and report identifier.

The mapping creates RDF resources for the installation, address, economic
activity and representative. It also links the installation to a GeoNames
country and enriches it with data from `CountryPlus.ttl`.

## Use

Ariadne reads `ariadne.yml`, loads the input files and writes the RDF graph to
`knowledgegraph/knowledge-graph.nt`.

For CI, set `QASAR_KEY` as a secret and `PIPELINE_IMAGE` as a repository
variable.
