<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('scan_logs', function (Blueprint $table) {
            $table->id('log_id');
            $table->string('scan_type', 10);
            $table->string('input_hash', 64)->index();
            $table->string('verdict', 20);
            $table->decimal('confidence_score', 5, 4)->nullable();
            $table->integer('scan_duration_ms');
            $table->timestamp('timestamp')->useCurrent();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('scan_logs');
    }
};