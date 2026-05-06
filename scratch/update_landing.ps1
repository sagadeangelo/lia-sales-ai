$files = Get-ChildItem -Path "D:\PROYECTOS_FLUTTER\lia-landing" -Filter "*.html"
foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    if ($content -notmatch "chat-widget.js") {
        $content = $content -replace '</body>', "`n  <!-- LIA SALES AI CHAT WIDGET -->`n  <script src=`"chat-widget.js`"></script>`n</body>"
        Set-Content $file.FullName $content
        Write-Host "Updated $($file.Name)"
    }
}
