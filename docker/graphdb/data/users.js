{
  "users" : {
    "admin" : {
      "username" : "admin",
      "password" : "{bcrypt}$2a$10$OfquFY8huzbknS3CD8.wv.lkL4j4B6zCoJJKUJ.j.SYt8NwqSALcO",
      "grantedAuthorities" : [ "ROLE_ADMIN" ],
      "appSettings" : {
        "DEFAULT_INFERENCE" : true,
        "DEFAULT_VIS_GRAPH_SCHEMA" : true,
        "DEFAULT_SAMEAS" : true,
        "IGNORE_SHARED_QUERIES" : false,
        "EXECUTE_COUNT" : true
      },
      "dateCreated" : 1708329238374
    },
    "pfr" : {
      "username" : "pfr",
      "password" : "{bcrypt}$2a$10$jJ/O6ywEIJtYDFKGX9dxzuI86N8wbtRvk.Oog140VB/AG81pFuht6",
      "grantedAuthorities" : [ "WRITE_REPO_pfr", "READ_REPO_pfr", "ROLE_USER" ],
      "appSettings" : {
        "DEFAULT_SAMEAS" : true,
        "DEFAULT_INFERENCE" : true,
        "EXECUTE_COUNT" : true,
        "IGNORE_SHARED_QUERIES" : false,
        "DEFAULT_VIS_GRAPH_SCHEMA" : true
      },
      "dateCreated" : 1708330767865
    }
  },
  "user_queries" : {
    "admin" : {
      "SPARQL Select template" : {
        "name" : "SPARQL Select template",
        "body" : "SELECT ?s ?p ?o\nWHERE {\n\t?s ?p ?o .\n} LIMIT 100",
        "shared" : false
      },
      "Clear graph" : {
        "name" : "Clear graph",
        "body" : "CLEAR GRAPH <http://example>",
        "shared" : false
      },
      "Add statements" : {
        "name" : "Add statements",
        "body" : "PREFIX dc: <http://purl.org/dc/elements/1.1/>\nINSERT DATA\n      {\n      GRAPH <http://example> {\n          <http://example/book1> dc:title \"A new book\" ;\n                                 dc:creator \"A.N.Other\" .\n          }\n      }",
        "shared" : false
      },
      "Remove statements" : {
        "name" : "Remove statements",
        "body" : "PREFIX dc: <http://purl.org/dc/elements/1.1/>\nDELETE DATA\n{\nGRAPH <http://example> {\n    <http://example/book1> dc:title \"A new book\" ;\n                           dc:creator \"A.N.Other\" .\n    }\n}",
        "shared" : false
      }
    }
  }
}