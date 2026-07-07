<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ScanController;

Route::any('/scan-url', [App\Http\Controllers\ScanController::class, 'scanUrl']);

Route::get('/debug-server', function () {
    // 1. Where is python3 installed?
    $pythonPath = shell_exec('which python3');
    // 2. What version is it?
    $pythonVer = shell_exec('python3 --version');
    // 3. Does the .joblib file actually exist on the server?
    $storageFiles = shell_exec('ls -la ' . storage_path('app'));
    
    return response()->json([
        'python_location' => trim($pythonPath) ?: 'NOT FOUND',
        'python_version' => trim($pythonVer) ?: 'NOT FOUND',
        'files_in_storage' => explode("\n", trim($storageFiles))
    ]);
});