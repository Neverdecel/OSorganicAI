-- ============================================
-- OSOrganicAI Database Schema
-- ============================================
-- This schema defines the database structure for OSOrganicAI.
-- Designed for Supabase (PostgreSQL with extensions).
--
-- Tables:
-- 1. conversations: Tracks issue requirement refinement conversations
-- 2. agent_actions: Logs all agent actions for audit and debugging
-- 3. code_generations: Tracks code generation and PR creation
--
-- Features:
-- - UUID primary keys for distributed systems
-- - JSONB for flexible schema
-- - Indexes for performance
-- - Timestamps for audit trail
-- - Row Level Security (RLS) policies
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- ============================================
-- Table: conversations
-- ============================================
-- Stores the state of ongoing conversations between
-- Product Owner Agent and users about issues.

CREATE TABLE IF NOT EXISTS conversations (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- GitHub Issue Information
    issue_id BIGINT NOT NULL,
    issue_number INTEGER NOT NULL,
    repo_full_name TEXT NOT NULL,

    -- Conversation State
    status TEXT NOT NULL DEFAULT 'analyzing',
    -- Status values: 'analyzing', 'needs_clarification', 'ready_for_dev', 'in_development', 'completed'

    -- Analysis Data (stored as JSONB for flexibility)
    analysis JSONB,
    -- Contains IssueAnalysis model data when available

    -- Conversation History
    turns JSONB DEFAULT '[]'::jsonb,
    -- Array of conversation turns

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT conversations_status_check CHECK (
        status IN ('analyzing', 'needs_clarification', 'ready_for_dev', 'in_development', 'completed')
    ),

    -- Unique constraint: one conversation per issue
    CONSTRAINT conversations_issue_unique UNIQUE (repo_full_name, issue_number)
);

-- Indexes for conversations
CREATE INDEX IF NOT EXISTS idx_conversations_issue_number
    ON conversations(issue_number);

CREATE INDEX IF NOT EXISTS idx_conversations_repo
    ON conversations(repo_full_name);

CREATE INDEX IF NOT EXISTS idx_conversations_status
    ON conversations(status);

CREATE INDEX IF NOT EXISTS idx_conversations_created_at
    ON conversations(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_updated_at
    ON conversations(updated_at DESC);

-- GIN index for JSONB analysis field (allows fast querying of nested data)
CREATE INDEX IF NOT EXISTS idx_conversations_analysis
    ON conversations USING GIN (analysis);

-- ============================================
-- Table: agent_actions
-- ============================================
-- Logs every action performed by agents for audit,
-- debugging, and analytics.

CREATE TABLE IF NOT EXISTS agent_actions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Key to conversation (optional - some actions may not be tied to a conversation)
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,

    -- Agent Information
    agent_type TEXT NOT NULL,
    -- e.g., 'ProductOwnerAgent', 'DeveloperAgent'

    action_type TEXT NOT NULL,
    -- e.g., 'issue_analyzed', 'questions_asked', 'code_generated', 'pr_created'

    -- Action Data (stored as JSONB)
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Contains action-specific data

    -- Execution Metadata
    status TEXT DEFAULT 'success',
    -- Values: 'success', 'failure', 'partial'

    error_message TEXT,
    -- Error details if status is 'failure'

    execution_time_ms INTEGER,
    -- Time taken to execute the action

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT agent_actions_status_check CHECK (
        status IN ('success', 'failure', 'partial')
    )
);

-- Indexes for agent_actions
CREATE INDEX IF NOT EXISTS idx_agent_actions_conversation_id
    ON agent_actions(conversation_id);

CREATE INDEX IF NOT EXISTS idx_agent_actions_agent_type
    ON agent_actions(agent_type);

CREATE INDEX IF NOT EXISTS idx_agent_actions_action_type
    ON agent_actions(action_type);

CREATE INDEX IF NOT EXISTS idx_agent_actions_status
    ON agent_actions(status);

CREATE INDEX IF NOT EXISTS idx_agent_actions_created_at
    ON agent_actions(created_at DESC);

-- GIN index for JSONB payload field
CREATE INDEX IF NOT EXISTS idx_agent_actions_payload
    ON agent_actions USING GIN (payload);

-- ============================================
-- Table: code_generations
-- ============================================
-- Tracks code generation results and pull requests.

CREATE TABLE IF NOT EXISTS code_generations (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Key to conversation
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,

    -- Pull Request Information
    pr_number INTEGER,
    pr_url TEXT,
    branch_name TEXT,

    -- Generated Code
    files_changed JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Array of FileChange objects

    tests_generated JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Array of TestFile objects

    -- Generation Metadata
    commit_message TEXT,
    pr_title TEXT,
    pr_description TEXT,

    -- Status
    status TEXT NOT NULL DEFAULT 'generated',
    -- Values: 'generated', 'pr_created', 'ci_passed', 'ci_failed', 'merged', 'closed'

    error_message TEXT,
    -- Error details if generation or PR creation failed

    -- Code Quality Metrics
    test_coverage_percentage FLOAT,
    estimated_complexity TEXT,
    -- Values: 'low', 'medium', 'high'

    -- Review Data (if self-review performed)
    review JSONB,
    -- Contains CodeReview model data

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT code_generations_status_check CHECK (
        status IN ('generated', 'pr_created', 'ci_passed', 'ci_failed', 'merged', 'closed', 'failed')
    ),

    CONSTRAINT code_generations_complexity_check CHECK (
        estimated_complexity IS NULL OR estimated_complexity IN ('low', 'medium', 'high')
    )
);

-- Indexes for code_generations
CREATE INDEX IF NOT EXISTS idx_code_generations_conversation_id
    ON code_generations(conversation_id);

CREATE INDEX IF NOT EXISTS idx_code_generations_pr_number
    ON code_generations(pr_number);

CREATE INDEX IF NOT EXISTS idx_code_generations_status
    ON code_generations(status);

CREATE INDEX IF NOT EXISTS idx_code_generations_created_at
    ON code_generations(created_at DESC);

-- GIN indexes for JSONB fields
CREATE INDEX IF NOT EXISTS idx_code_generations_files_changed
    ON code_generations USING GIN (files_changed);

CREATE INDEX IF NOT EXISTS idx_code_generations_tests_generated
    ON code_generations USING GIN (tests_generated);

CREATE INDEX IF NOT EXISTS idx_code_generations_review
    ON code_generations USING GIN (review);

-- ============================================
-- Functions and Triggers
-- ============================================

-- Function to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for conversations table
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for code_generations table
DROP TRIGGER IF EXISTS update_code_generations_updated_at ON code_generations;
CREATE TRIGGER update_code_generations_updated_at
    BEFORE UPDATE ON code_generations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Row Level Security (RLS) Policies
-- ============================================
-- Enable RLS for all tables (customize based on your auth setup)

-- Note: These policies are templates. Adjust based on your authentication strategy.
-- For now, we'll enable RLS but allow all operations with service role key.

ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE code_generations ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for service role
CREATE POLICY "Enable all operations for service role" ON conversations
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Enable all operations for service role" ON agent_actions
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Enable all operations for service role" ON code_generations
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Policy: Allow read access for authenticated users (optional)
-- Uncomment if you want users to view conversation data
-- CREATE POLICY "Enable read access for authenticated users" ON conversations
--     FOR SELECT
--     TO authenticated
--     USING (true);

-- ============================================
-- Useful Views (Optional)
-- ============================================

-- View: Recent agent activity
CREATE OR REPLACE VIEW recent_agent_activity AS
SELECT
    aa.id,
    aa.agent_type,
    aa.action_type,
    aa.status,
    aa.created_at,
    c.issue_number,
    c.repo_full_name,
    c.status as conversation_status
FROM agent_actions aa
LEFT JOIN conversations c ON aa.conversation_id = c.id
ORDER BY aa.created_at DESC
LIMIT 100;

-- View: Conversation summary
CREATE OR REPLACE VIEW conversation_summary AS
SELECT
    c.id as conversation_id,
    c.issue_number,
    c.repo_full_name,
    c.status,
    c.created_at,
    c.updated_at,
    COUNT(DISTINCT aa.id) as action_count,
    MAX(aa.created_at) as last_action_at,
    CASE
        WHEN cg.id IS NOT NULL THEN TRUE
        ELSE FALSE
    END as has_code_generation,
    cg.pr_number,
    cg.status as code_generation_status
FROM conversations c
LEFT JOIN agent_actions aa ON aa.conversation_id = c.id
LEFT JOIN code_generations cg ON cg.conversation_id = c.id
GROUP BY c.id, c.issue_number, c.repo_full_name, c.status,
         c.created_at, c.updated_at, cg.id, cg.pr_number, cg.status;

-- ============================================
-- Grants (Adjust based on your setup)
-- ============================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO service_role;
GRANT USAGE ON SCHEMA public TO authenticated;

-- Grant table permissions
GRANT ALL ON conversations TO service_role;
GRANT ALL ON agent_actions TO service_role;
GRANT ALL ON code_generations TO service_role;

-- Grant select on views
GRANT SELECT ON recent_agent_activity TO service_role;
GRANT SELECT ON conversation_summary TO service_role;

-- ============================================
-- Sample Queries (for reference)
-- ============================================

-- Find all conversations for a repo
-- SELECT * FROM conversations WHERE repo_full_name = 'owner/repo' ORDER BY created_at DESC;

-- Get conversation with all actions
-- SELECT c.*, array_agg(aa.*) as actions
-- FROM conversations c
-- LEFT JOIN agent_actions aa ON aa.conversation_id = c.id
-- WHERE c.issue_number = 42 AND c.repo_full_name = 'owner/repo'
-- GROUP BY c.id;

-- Find failed actions
-- SELECT * FROM agent_actions WHERE status = 'failure' ORDER BY created_at DESC;

-- Get code generation success rate
-- SELECT
--   status,
--   COUNT(*) as count,
--   ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
-- FROM code_generations
-- GROUP BY status;
