from SPARQLWrapper import SPARQLWrapper, JSON

# TODO cache ?
def query_pop5():
    URL = "http://graphdb.linked-open-statistics.org/repositories/pop5"

    QUERY = """
    PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX cog2017: <http://id.insee.fr/codes/cog2017/>
    SELECT ?id ?code
    WHERE {
        ?id skos:notation ?code ;
        rdf:type cog2017:DepartementOuCommuneOuArrondissementMunicipal .
    } LIMIT 100
    """

    # The SPARQLWrapper will store network info and query logic
    hackathon_endpoint = SPARQLWrapper(URL)
    hackathon_endpoint.setQuery(QUERY)

    # We want the resulting data in JSON format
    hackathon_endpoint.setReturnFormat(JSON)
    query_res = hackathon_endpoint.query().convert()

    # Data structures for storing codes and URIs
    uris = []
    codes = []
    for results in query_res["results"]["bindings"]:
        code = results['code']['value']
        codes.append(code)
        uri = results['id']['value']
        uris.append(uri)
    
    return codes

def query_datasets():
    URL = "http://hackathon2018.ontotext.com/repositories/plosh"

    QUERY = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX qb: <http://purl.org/linked-data/cube#>
    PREFIX mes: <http://id.insee.fr/meta/mesure/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 

    SELECT ?dataset_uri ?label  where {           
        ?dataset_uri a qb:DataSet .
        OPTIONAL{ 
            ?dataset_uri rdfs:label ?label 
            filter(langMatches(lang(?label),"fr"))
            
        }
    }
    """

    wrapper = SPARQLWrapper(URL)
    wrapper.setQuery(QUERY)
    wrapper.setReturnFormat(JSON)
    json = wrapper.query().convert()

    def label_modif(row):
        if "label" in row.keys():
            return row["label"]["value"] 
        else:
            return row["dataset_uri"]["value"]

    return [ {"label": label_modif(row), "value": label_modif(row)} for row in json["results"]["bindings"] ] 
 
from SPARQLWrapper import SPARQLWrapper, JSON

#if the arg is empty in ProxyHandler, urllib will find itself your proxy config.
proxy_support = urllib.request.ProxyHandler({'http':'http://proxy-rie.http.insee.fr:8080', 'https':'http://proxy-rie.http.insee.fr:8080'})
opener = urllib.request.build_opener(proxy_support)
urllib.request.install_opener(opener)

sparql = SPARQLWrapper("http://hackathon2018.ontotext.com/repositories/plosh")
sparql.setReturnFormat(JSON)

def query_dimensions():
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX qb: <http://purl.org/linked-data/cube#>
    PREFIX mes: <http://id.insee.fr/meta/mesure/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 

    SELECT ?dim ?label where {           
        ?s a qb:DataSet.
        ?s qb:structure ?dsd.
        ?dsd qb:component/qb:dimension ?dim.
        ?dim rdfs:label ?labelfr

        filter(langMatches(lang(?labelfr),"fr"))
        BIND(IF(BOUND(?labelfr), ?labelfr,?dim) AS ?label)
    }  LIMIT 10
    """

    sparql.setQuery(query)
    results = sparql.query().convert()

    results=query_dimensions()['results']['bindings']
    keys=list(results[0].keys())  
    
    return [{'label': result[keys[1]]['value'], 'value': result[keys[0]]['value']} for result in results]
    
