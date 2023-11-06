CREATE TABLE datasets (
    dataset_id TEXT NOT NULL,
    name TEXT NOT NULL,
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

CREATE TABLE documents (
    document_id text not null,
    dataset_id text not null,
    title text not null,
    primary key (document_id)
);

CREATE TABLE pages (
    document_id text not null,
    page_nr integer not null,
    image_path text not null,
    page_width double precision not null,
    page_height double precision not null,
    n_horizontal_lines integer not null,
    avg_char_size double precision not null,
    median_char_size double precision not null,
    primary key (document_id, page_nr)
);

CREATE TABLE lines (
    document_id text not null,
    page_nr integer not null,
    line_nr integer not null,
    line_text text not null,
    x double precision not null,
    y double precision not null,
    width double precision not null,
    height double precision not null,
    n_lines_below integer not null,
    avg_char_size double precision not null,
    median_char_size double precision not null,
    merged integer[] not null default ARRAY[]::integer[],
    label integer default -1,
    primary key (document_id, page_nr, line_nr)
);

CREATE TABLE chars (
    document_id text not null,
    page_nr integer not null,
    char_nr integer not null,
    char_text text not null,
    x double precision not null,
    y double precision not null,
    width double precision not null,
    height double precision not null,
    label integer default -1,
    primary key (document_id, page_nr, char_nr)
);