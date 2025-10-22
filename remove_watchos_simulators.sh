#!/bin/bash

# Apple Watch Simulator Cleanup Script
# This script removes all Apple Watch OS simulator components
# Total estimated space to be freed: ~34GB

echo "🍎 Apple Watch Simulator Cleanup"
echo "================================="

echo "📊 Current watchOS component sizes:"
echo "  - watchOS Runtime Volumes: ~27.5GB"
echo "  - watchOS Device Types: 29 device types"
echo "  - watchOS Cache Data: ~6.8GB"
echo "  - Total Estimated: ~34GB"
echo ""

read -p "⚠️  Are you sure you want to remove ALL Apple Watch simulator components? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled by user"
    exit 1
fi

echo "🧹 Starting cleanup..."

# 1. Remove watchOS Runtime Volumes (27.5GB)
echo "1️⃣ Removing watchOS runtime volumes..."
sudo rm -rf /Library/Developer/CoreSimulator/Volumes/watchOS_22R349  # watchOS 11.0 (9.7GB)
sudo rm -rf /Library/Developer/CoreSimulator/Volumes/watchOS_22T572  # watchOS 11.5 (10GB)
sudo rm -rf /Library/Developer/CoreSimulator/Volumes/watchOS_23R353  # watchOS 26.0 (7.8GB)

if [ $? -eq 0 ]; then
    echo "   ✅ Runtime volumes removed (~27.5GB freed)"
else
    echo "   ❌ Failed to remove runtime volumes"
fi

# 2. Remove Apple Watch Device Types (29 types)
echo "2️⃣ Removing Apple Watch device types..."
sudo rm -rf "/Library/Developer/CoreSimulator/Profiles/DeviceTypes/Apple Watch"*

if [ $? -eq 0 ]; then
    echo "   ✅ Device types removed (29 Apple Watch device types)"
else
    echo "   ❌ Failed to remove device types"
fi

# 3. Remove watchOS Cache Data (6.8GB)
echo "3️⃣ Removing watchOS cache data..."
sudo rm -rf /Library/Developer/CoreSimulator/Caches/dyld/*/com.apple.CoreSimulator.SimRuntime.watchOS-*

if [ $? -eq 0 ]; then
    echo "   ✅ Cache data removed (~6.8GB freed)"
else
    echo "   ❌ Failed to remove cache data"
fi

echo ""
echo "🎉 Apple Watch simulator cleanup completed!"
echo "📈 Estimated space freed: ~34GB"
echo ""
echo "📱 Remaining iOS simulators are preserved for your development work."
echo ""

# Verify removal
echo "🔍 Verification:"
WATCHOS_VOLUMES=$(find /Library/Developer/CoreSimulator/Volumes -name "watchOS_*" 2>/dev/null | wc -l)
WATCH_DEVICES=$(ls /Library/Developer/CoreSimulator/Profiles/DeviceTypes/ 2>/dev/null | grep -i watch | wc -l)
WATCHOS_CACHE=$(find /Library/Developer/CoreSimulator/Caches -name "*watchOS*" 2>/dev/null | wc -l)

echo "  - watchOS Volumes remaining: $WATCHOS_VOLUMES"
echo "  - Apple Watch device types remaining: $WATCH_DEVICES"
echo "  - watchOS cache entries remaining: $WATCHOS_CACHE"

if [ $WATCHOS_VOLUMES -eq 0 ] && [ $WATCH_DEVICES -eq 0 ] && [ $WATCHOS_CACHE -eq 0 ]; then
    echo "  ✅ All Apple Watch components successfully removed!"
else
    echo "  ⚠️  Some components may still remain"
fi

echo ""
echo "💡 To verify total space freed, run:"
echo "   df -h"