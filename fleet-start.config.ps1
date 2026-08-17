# Per-repo fleet start config for sakana-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'sakana-mcp'
    BackendPort  = 10863
    FrontendPort = 10862
    HealthPath   = '/api/health'
    WebRoot      = 'D:\Dev\repos\sakana-mcp\webapp\frontend'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'app:app'
        WorkDir       = 'D:\Dev\repos\sakana-mcp\webapp\backend'
        UvProject     = 'D:\Dev\repos\sakana-mcp'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10863' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
