<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class ScanController extends Controller
{
    public function scanUrl(Request $request)
    {
        $request->validate([
            'url' => 'required|string'
        ]);

        $targetUrl = $request->input('url');

        // Initialize the process
        $process = new Process(['C:\\Python314\\python.exe', base_path('scripts/api_bridge.py'), $targetUrl]);
        $process->setTimeout(15); 

        // 🛠️ CRUCIAL WINDOWS ENVIRONMENT FIX
        // This injects Windows core system paths so Python's asyncio layer can load properly
        $process->setEnv([
            'SystemRoot' => 'C:\\Windows',
            'System32' => 'C:\\Windows\\System32',
            'PATH' => getenv('PATH')
        ]);

        try {
            $process->mustRun();
            $output = $process->getOutput();

            $result = json_decode($output, true);

            if (json_last_error() !== JSON_ERROR_NONE) {
                return response()->json([
                    'error' => 'Failed to parse AI output.',
                    'raw_output' => $output
                ], 500);
            }

            return response()->json($result, 200);

        } catch (ProcessFailedException $exception) {
            return response()->json([
                'error' => 'CheckDulu AI Engine Execution Failed.',
                'details' => $exception->getMessage()
            ], 500);
        }
    }
}