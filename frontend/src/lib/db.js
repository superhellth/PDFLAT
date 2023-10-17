
import pg from 'pg';
const { Pool } = pg;

const pool = new Pool({
    database: "test_db",
    user: "test_user",
    host: "pg-db",
    password: "PG_PASSWORD",
    port: 5432,
    max: 100
});
export const connectToDB = () => {
    return pool.connect()
};