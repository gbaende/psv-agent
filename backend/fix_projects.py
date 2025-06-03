#!/usr/bin/env python3
"""
Fix duplicate projects issue
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.database import DATABASE_URL

async def fix_projects():
    """Fix duplicate projects and clean up database"""
    
    print("🔧 Fixing duplicate projects...")
    print("=" * 50)
    
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # Check current projects
        result = await conn.execute(text('SELECT id, name FROM projects ORDER BY id'))
        projects = result.fetchall()
        print(f"Current projects ({len(projects)}):")
        for project in projects:
            print(f"  ID: {project[0]}, Name: {project[1]}")
        
        # Delete duplicate "Sales Sprint" projects (keep only the PSV Sales Agent Team)
        print(f"\n🧹 Removing duplicate 'Sales Sprint' projects...")
        
        # First, update any tasks that reference the duplicate projects to use project ID 1
        result = await conn.execute(text('UPDATE tasks SET project_id = 1 WHERE project_id IN (2, 3)'))
        print(f"   ✅ Updated {result.rowcount} tasks to use project ID 1")
        
        # Delete the duplicate projects
        result = await conn.execute(text('DELETE FROM projects WHERE id IN (2, 3)'))
        print(f"   ✅ Deleted {result.rowcount} duplicate projects")
        
        # Verify the fix
        result = await conn.execute(text('SELECT id, name FROM projects ORDER BY id'))
        projects = result.fetchall()
        print(f"\n✅ Projects after cleanup ({len(projects)}):")
        for project in projects:
            print(f"  ID: {project[0]}, Name: {project[1]}")
        
        # Check tasks
        result = await conn.execute(text('SELECT COUNT(*) as count, project_id FROM tasks GROUP BY project_id'))
        task_counts = result.fetchall()
        print(f"\n📋 Tasks by project:")
        for count, project_id in task_counts:
            print(f"  Project {project_id}: {count} tasks")
    
    await engine.dispose()
    print(f"\n🎉 **PROJECT CLEANUP SUCCESSFUL!**")
    print(f"✅ Duplicate projects removed")
    print(f"✅ All tasks now reference the correct project")

if __name__ == "__main__":
    asyncio.run(fix_projects()) 