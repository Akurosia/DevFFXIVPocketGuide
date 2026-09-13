# frozen_string_literal: true

# Work around a Liquid 4.0.4 / Ruby 3.3 failure while Liquid calculates the
# resource "assign score" of nested Hash values:
#
#   RuntimeError: hash representation was changed during iteration
#
# Liquid 4.0.4 iterates the live Hash recursively in Assign#assign_score_of.
# Some of the deeply nested guide data can cause Ruby 3.3 to change the
# internal Hash representation during that traversal.
#
# Snapshotting the Hash entries first keeps Liquid's scoring semantics while
# avoiding iteration over a live Hash that may change representation.

require "liquid"

module DevFFXIVPocketGuide
  module SafeLiquidAssignScore
    private

    def assign_score_of(value)
      case value
      when String
        value.bytesize
      when Array
        # Snapshot for the same reason as Hash below. The extra allocation is
        # small compared with rendering the guide pages and only happens for
        # Liquid {% assign %} resource accounting.
        value.to_a.sum(1) { |child| assign_score_of(child) }
      when Hash
        # Critical part: never recurse while iterating the live Hash.
        value.to_a.sum(1) do |key, entry_value|
          assign_score_of(key) + assign_score_of(entry_value)
        end
      else
        1
      end
    end
  end
end

unless Liquid::Assign.ancestors.include?(DevFFXIVPocketGuide::SafeLiquidAssignScore)
  Liquid::Assign.prepend(DevFFXIVPocketGuide::SafeLiquidAssignScore)
end
