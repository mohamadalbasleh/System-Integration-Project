$ErrorActionPreference = "Stop"

$pgBin = "C:\Program Files\PostgreSQL\18\bin"
$env:PGPASSWORD = if ($env:PGPASSWORD) { $env:PGPASSWORD } else { "123" }
$dbName = "online_bookstore_db"

$dbExists = & "$pgBin\psql.exe" -h localhost -U postgres -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$dbName';"
if (-not $dbExists) {
    & "$pgBin\createdb.exe" -h localhost -U postgres $dbName
}

& "$pgBin\psql.exe" -h localhost -U postgres -d $dbName -f (Join-Path $PSScriptRoot "schema.sql")
& "$pgBin\psql.exe" -h localhost -U postgres -d $dbName -f (Join-Path $PSScriptRoot "seed.sql")
& "$pgBin\psql.exe" -h localhost -U postgres -d $dbName -f (Join-Path $PSScriptRoot "verification_queries.sql")

Write-Host "Database setup complete for $dbName"
