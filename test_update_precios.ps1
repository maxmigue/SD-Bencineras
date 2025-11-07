$body = @{
  precios = @{
    precio_93 = 1500
    precio_95 = 1550
    precio_97 = 1600
    precio_diesel = 1200
  }
} | ConvertTo-Json -Depth 3

Write-Host "📤 Enviando actualización de precios..."
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/estaciones/1/precios" -Method Put -Body $body -ContentType "application/json"
Write-Host "✅ Respuesta recibida:"
$response | ConvertTo-Json -Depth 5
