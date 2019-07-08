This folder provides PostgreSQL statements, queries and functions to

- set up the **`data model`** required for OBIA4RTM (see ./Tables)

- set up functions for the **`parameter retrieval`** and queries to obtain results from the database (./Queries_Functions)

By default, the **`public`**-Schema will be used for all the *general metadata*.
The results are stored in **`obia4rtm_xx`**, where *_xx* denotes a placeholder for a user-defined name of the schema. Within a schema,
the ID for *object* must be **unique**. It is therefore suggested to create this schema for particular regions of interest (ROI) independently.
