const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const dbPath = path.join(__dirname, '..', 'data', 'youthmind.db');
const sqlPath = path.join(__dirname, '..', 'database', 'sqlite', 'init.sql');

const dataDir = path.dirname(dbPath);
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

const db = new Database(dbPath);

const sql = fs.readFileSync(sqlPath, 'utf-8');

const statements = sql
  .split(';')
  .map(s => s.trim())
  .filter(s => s.length > 0 && !s.startsWith('--'));

console.log('Initializing database...');

for (const statement of statements) {
  try {
    db.exec(statement + ';');
  } catch (error) {
    console.error('Error executing statement:', error.message);
  }
}

console.log('Database initialized successfully!');
console.log('Database location:', dbPath);

db.close();
