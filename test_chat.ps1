#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Test Auto-Ops-AI Multi-Agent Chat System
.DESCRIPTION
    Demonstrates the complete multi-agent IT support system
#>

Write-Host "🤖 Auto-Ops-AI Multi-Agent Chat System Test" -ForegroundColor Cyan
Write-Host "=" * 60

$baseUrl = "http://127.0.0.1:8000/api/v1"

# Test 1: Simple issue - should work immediately
Write-Host "`n📝 Test 1: Clear Issue (Network)" -ForegroundColor Yellow
Write-Host "-" * 60

$request1 = @{
    messages = @(
        @{
            role = "user"
            content = "I cannot connect to VPN. Getting 'authentication failed' error since this morning."
        }
    )
    user_email = "alice@acme-soft.com"
} | ConvertTo-Json -Depth 10

try {
    $response1 = Invoke-RestMethod -Uri "$baseUrl/chat" -Method Post -Body $request1 -ContentType "application/json"
    
    Write-Host "✅ Response:" -ForegroundColor Green
    Write-Host $response1.message
    Write-Host "`n📋 Ticket ID: $($response1.ticket_id)" -ForegroundColor Cyan
    Write-Host "🎯 Action: $($response1.action)" -ForegroundColor Cyan
    Write-Host "⚡ Priority: $($response1.priority_info.priority_label)" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

# Test 2: Vague issue - should ask clarifying questions
Write-Host "`n`n📝 Test 2: Vague Issue (Needs Clarification)" -ForegroundColor Yellow
Write-Host "-" * 60

$request2 = @{
    messages = @(
        @{
            role = "user"
            content = "My laptop is slow"
        }
    )
    user_email = "bob@acme-soft.com"
} | ConvertTo-Json -Depth 10

try {
    $response2 = Invoke-RestMethod -Uri "$baseUrl/chat" -Method Post -Body $request2 -ContentType "application/json"
    
    Write-Host "✅ Response:" -ForegroundColor Green
    Write-Host $response2.message
    Write-Host "`n🔍 Needs Clarification: $($response2.needs_clarification)" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

# Test 3: Critical issue from manager - should escalate
Write-Host "`n`n📝 Test 3: Critical Issue (Manager)" -ForegroundColor Yellow
Write-Host "-" * 60

$request3 = @{
    messages = @(
        @{
            role = "user"
            content = "URGENT! My laptop has blue screen (BSOD) during client meeting. I have a presentation in 30 minutes!"
        }
    )
    user_email = "carol.johnson@acme-soft.com"  # Manager in dataset
} | ConvertTo-Json -Depth 10

try {
    $response3 = Invoke-RestMethod -Uri "$baseUrl/chat" -Method Post -Body $request3 -ContentType "application/json"
    
    Write-Host "✅ Response:" -ForegroundColor Green
    Write-Host $response3.message
    Write-Host "`n📋 Ticket ID: $($response3.ticket_id)" -ForegroundColor Cyan
    Write-Host "🎯 Action: $($response3.action)" -ForegroundColor Cyan
    Write-Host "⚡ Priority: $($response3.priority_info.priority_label)" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

# Test 4: Check tickets created
Write-Host "`n`n📊 Tickets Created" -ForegroundColor Yellow
Write-Host "-" * 60

try {
    $tickets = Invoke-RestMethod -Uri "$baseUrl/tickets" -Method Get
    
    Write-Host "✅ Total tickets: $($tickets.Count)" -ForegroundColor Green
    
    foreach ($ticket in $tickets | Select-Object -First 5) {
        Write-Host "`nTicket #$($ticket.id):" -ForegroundColor Cyan
        Write-Host "  Title: $($ticket.title)"
        Write-Host "  Status: $($ticket.status)"
        Write-Host "  Priority: $($ticket.priority)"
        Write-Host "  User: $($ticket.user_email)"
    }
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Write-Host "`n`n" + "=" * 60
Write-Host "✅ Tests completed! Check API docs at: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "=" * 60
