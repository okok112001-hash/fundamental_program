# Human-only actions (short list)

Do only these things:

1. Approve the frozen spec version for build.
2. Approve the data providers your team will actually pay for and use.
3. Approve the golden routing set as the first acceptance test set.
4. Review only these outputs from implementation:
   - template_id
   - routing_reason
   - status / gate_stage
   - scores nullability
   - confidence nullability
5. Decide whether each weekly build is:
   - accepted
   - accepted with notes
   - rejected

You do **not** need to manage low-level implementation details.
