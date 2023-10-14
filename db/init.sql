CREATE TABLE datasets (
    dataset_id TEXT NOT NULL,
    name TEXT NOT NULL,
    test_percentage INTEGER NOT NULL DEFAULT 10,
    eval_percentage INTEGER NOT NULL DEFAULT 10,
    labels JSONB[] NOT NULL DEFAULT ARRAY[
        '{
            "id": 0,
            "name": "text",
            "color": "blue"
        }'::JSONB,
        '{
            "id": 1,
            "name": "title",
            "color": "red"
        }'::JSONB,
        '{
            "id": 2,
            "name": "table",
            "color": "green"
        }'::JSONB,
        '{
            "id": 3,
            "name": "list",
            "color": "purple"
        }'::JSONB,
        '{
            "id": 4,
            "name": "caption",
            "color": "orange"
        }'::JSONB,
        '{
            "id": 5,
            "name": "page_nr",
            "color": "yellow"
        }'::JSONB,
        '{
            "id": 6,
            "name": "footnote",
            "color": "sky"
        }'::JSONB,
        '{
            "id": 7,
            "name": "formular",
            "color": "lime"
        }'::JSONB,
        '{
            "id": -1,
            "name": "none",
            "color": "gray"
        }'::JSONB
    ],
    PRIMARY KEY (dataset_id)
);

CREATE TABLE models (
    model_id TEXT NOT NULL,
    graph_type TEXT NOT NULL,
    parameters json NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (model_id)
);

CREATE TABLE dataset_models (
    model_id TEXT NOT NULL,
    dataset_id TEXT NOT NULL,
    train_ids TEXT[] NOT NULL,
    test_ids TEXT[] NOT NULL,
    eval_ids TEXT[] NOT NULL,
    num_classes INTEGER NOT NULL,
    num_node_features INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    test_results json NOT NULL default '{}',
    eval_results json NOT NULL default '{}',
    PRIMARY KEY (model_id, dataset_id)
);

CREATE TABLE documents (
    dataset_id text not null,
    document_id text not null,
    title text not null,
    primary key (document_id)
);

CREATE TABLE pages (
    document_id text not null,
    page_nr integer not null,
    page_width double precision not null,
    page_height double precision not null,
    number_nodes integer not null,
    image_path text not null,
    nodes json[] not null default ARRAY[]::JSON[],
    graphs json not null default '{
        "fully_connected": [],
        "visibility": [],
        "2NN": [],
        "3NN": []
    }',
    labelled bool not null default false,
    primary key (document_id, page_nr)
);

CREATE TABLE nodes (
    document_id text not null,
    page_nr integer not null,
    /*block_nr integer not null,
     line_nr integer not null,*/
    node_nr integer not null,
    x_min double precision not null,
    x_max double precision not null,
    y_min double precision not null,
    y_max double precision not null,
    features json not null,
    width double precision not null,
    height double precision not null,
    primary key (document_id, page_nr, node_nr)
);

CREATE TABLE regions (
    document_id text not null,
    page_nr integer not null,
    region_id text not null,
    x_min double precision not null,
    x_max double precision not null,
    y_min double precision not null,
    y_max double precision not null,
    width double precision not null,
    height double precision not null,
    label integer default -1,
    nodes json[] not null default ARRAY[]::JSON[],
    graphs json not null default '{
        "fully_connected": [],
        "visibility": [],
        "2NN": [],
        "3NN": []
    }',
    primary key (region_id)
);