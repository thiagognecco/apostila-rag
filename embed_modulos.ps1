# Script PowerShell para embutir módulos no HTML

$htmlPath = "index.html"
$htmlContent = Get-Content $htmlPath -Raw

# Lê todos os módulos
$modulosObj = @{}
1..15 | ForEach-Object {
    $path = "modulo_$_.md"
    if (Test-Path $path) {
        $content = Get-Content $path -Raw
        $modulosObj[$_] = $content
    }
}

# Cria script inline
$modulosJson = $modulosObj | ConvertTo-Json
$scriptInline = @"
<script>
let modulosConteudo = JSON.parse('$($modulosJson -replace "'", "\'")');
</script>
"@

# Insere antes de </head>
$htmlNew = $htmlContent -replace '</head>', "$scriptInline`n</head>"

Set-Content $htmlPath -Value $htmlNew
Write-Host "✅ Módulos embedados no HTML"
